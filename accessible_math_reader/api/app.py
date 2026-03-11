"""!
@file api/app.py
@brief REST API Blueprint for Accessible Math Reader.

@details
Exposes the full AMR pipeline as a versioned JSON REST API.

Endpoints (all under ``/api/v1/``):
  POST /api/v1/speech     — convert math to spoken English
  POST /api/v1/braille    — convert math to Braille
  POST /api/v1/structure  — return the semantic AST as JSON
  POST /api/v1/audio      — synthesise speech and return MP3 binary
  POST /api/v1/validate   — run accessibility validation

Infrastructure routes (mounted at root):
  GET  /health            — liveness probe  (Feature 6)
  GET  /readiness         — readiness probe (Feature 6)
  GET  /metrics           — Prometheus text exposition (Feature 7)

All conversion endpoints reuse ``MathReader`` from the core library —
no logic is duplicated.

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import io
import logging
import os
import tempfile
import time
from typing import Any

from flask import Blueprint, Response, jsonify, request, send_file

from accessible_math_reader.api.errors import (
    ErrorCode,
    error_response,
    register_error_handlers,
)
from accessible_math_reader.api.middleware import rate_limit, require_api_key
from accessible_math_reader.api.schemas import (
    braille_response,
    speech_response,
    structure_response,
    validate_math_request,
    validation_response,
)
from accessible_math_reader.observability.metrics import MetricsCollector

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singletons (instantiated at import time)
# ---------------------------------------------------------------------------

_metrics = MetricsCollector()


# ---------------------------------------------------------------------------
# Blueprint factory
# ---------------------------------------------------------------------------

def create_api_blueprint() -> Blueprint:
    """!
    @brief Create and return the REST API Blueprint.

    @details
    Register this blueprint on any Flask app:

    @code{.py}
    from accessible_math_reader.api import create_api_blueprint

    app = Flask(__name__)
    app.register_blueprint(create_api_blueprint())
    @endcode

    @return Configured Flask Blueprint
    """
    bp = Blueprint("amr_api", __name__)
    register_error_handlers(bp)

    # ── Lazy reader accessor ──────────────────────────────────────
    _reader_cache: dict[str, Any] = {}

    def _get_reader() -> Any:
        """Get or create a shared MathReader instance."""
        if "reader" not in _reader_cache:
            from accessible_math_reader.reader import MathReader
            _reader_cache["reader"] = MathReader()
        return _reader_cache["reader"]

    # ══════════════════════════════════════════════════════════════
    # Conversion Endpoints  (/api/v1/…)
    # ══════════════════════════════════════════════════════════════

    @bp.route("/api/v1/speech", methods=["POST"])
    @require_api_key
    @rate_limit
    def api_speech() -> Any:
        """!
        @brief Convert math input to spoken English text.

        @details
        Accepts JSON: ``{"input": "...", "format": "auto"}``
        Returns JSON: ``{"speech": "...", "input": "..."}``
        """
        _metrics.inc_request("speech")
        data = request.get_json(silent=True)
        err, params = validate_math_request(data)
        if err:
            return error_response(err, ErrorCode.VALIDATION_ERROR, 400)

        try:
            reader = _get_reader()
            with _metrics.timer("speech"):
                text = reader.to_speech(params["input"])
            return jsonify(speech_response(text, params["input"]))
        except Exception as exc:
            logger.exception("Speech conversion failed")
            _metrics.inc_error("speech_error")
            return error_response(
                str(exc), ErrorCode.PARSE_ERROR, 422
            )

    @bp.route("/api/v1/braille", methods=["POST"])
    @require_api_key
    @rate_limit
    def api_braille() -> Any:
        """!
        @brief Convert math input to Braille notation.

        @details
        Accepts JSON: ``{"input": "...", "notation": "nemeth"}``
        Returns JSON: ``{"braille": "...", "notation": "...", "input": "..."}``
        """
        _metrics.inc_request("braille")
        data = request.get_json(silent=True)
        err, params = validate_math_request(data)
        if err:
            return error_response(err, ErrorCode.VALIDATION_ERROR, 400)

        try:
            reader = _get_reader()
            with _metrics.timer("braille"):
                text = reader.to_braille(
                    params["input"], notation=params["notation"]
                )
            return jsonify(
                braille_response(text, params["notation"], params["input"])
            )
        except Exception as exc:
            logger.exception("Braille conversion failed")
            _metrics.inc_error("braille_error")
            return error_response(
                str(exc), ErrorCode.PARSE_ERROR, 422
            )

    @bp.route("/api/v1/structure", methods=["POST"])
    @require_api_key
    @rate_limit
    def api_structure() -> Any:
        """!
        @brief Return the semantic AST of a math expression as JSON.

        @details
        Accepts JSON: ``{"input": "..."}``
        Returns JSON: ``{"structure": {...}, "input": "..."}``
        """
        _metrics.inc_request("structure")
        data = request.get_json(silent=True)
        err, params = validate_math_request(data)
        if err:
            return error_response(err, ErrorCode.VALIDATION_ERROR, 400)

        try:
            reader = _get_reader()
            with _metrics.timer("structure"):
                struct = reader.get_structure(params["input"])
            return jsonify(structure_response(struct, params["input"]))
        except Exception as exc:
            logger.exception("Structure extraction failed")
            _metrics.inc_error("structure_error")
            return error_response(
                str(exc), ErrorCode.PARSE_ERROR, 422
            )

    @bp.route("/api/v1/audio", methods=["POST"])
    @require_api_key
    @rate_limit
    def api_audio() -> Any:
        """!
        @brief Synthesise math speech and return an MP3 file.

        @details
        Accepts JSON: ``{"input": "..."}``
        Returns: binary MP3 with ``Content-Type: audio/mpeg``
        """
        _metrics.inc_request("audio")
        data = request.get_json(silent=True)
        err, params = validate_math_request(data)
        if err:
            return error_response(err, ErrorCode.VALIDATION_ERROR, 400)

        try:
            reader = _get_reader()
            with _metrics.timer("audio"):
                # Create a temp file for the audio
                tmp = tempfile.NamedTemporaryFile(
                    suffix=".mp3", delete=False
                )
                tmp_path = tmp.name
                tmp.close()
                reader.to_audio(params["input"], tmp_path)

            return send_file(
                tmp_path,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name="speech.mp3",
            )
        except Exception as exc:
            logger.exception("Audio synthesis failed")
            _metrics.inc_error("audio_error")
            return error_response(
                str(exc), ErrorCode.INTERNAL_ERROR, 500
            )

    @bp.route("/api/v1/validate", methods=["POST"])
    @require_api_key
    @rate_limit
    def api_validate() -> Any:
        """!
        @brief Run accessibility validation on a math expression.

        @details
        Accepts JSON: ``{"input": "..."}``
        Returns JSON:
        @code{.json}
        {
          "wcag_violations": [],
          "missing_semantic_structure": [],
          "aria_warnings": [],
          "valid": true
        }
        @endcode
        """
        _metrics.inc_request("validate")
        data = request.get_json(silent=True)
        err, params = validate_math_request(data)
        if err:
            return error_response(err, ErrorCode.VALIDATION_ERROR, 400)

        try:
            from accessible_math_reader.validation.validator import (
                MathValidator,
            )

            with _metrics.timer("validate"):
                validator = MathValidator()
                results = validator.validate_expression(params["input"])
            return jsonify(validation_response(results))
        except Exception as exc:
            logger.exception("Validation failed")
            _metrics.inc_error("validate_error")
            return error_response(
                str(exc), ErrorCode.INTERNAL_ERROR, 500
            )

    # ══════════════════════════════════════════════════════════════
    # Infrastructure Endpoints  (Feature 6 — Kubernetes)
    # ══════════════════════════════════════════════════════════════

    @bp.route("/health", methods=["GET"])
    def health() -> Any:
        """!
        @brief Liveness probe — returns 200 if the process is alive.
        """
        return jsonify({"status": "healthy", "timestamp": time.time()})

    @bp.route("/readiness", methods=["GET"])
    def readiness() -> Any:
        """!
        @brief Readiness probe — returns 200 if the service can accept requests.

        @details
        Checks that the core pipeline can be initialised.  Returns 503
        if something is wrong.
        """
        try:
            _get_reader()
            return jsonify({"status": "ready", "timestamp": time.time()})
        except Exception as exc:
            return jsonify({
                "status": "not ready",
                "error": str(exc),
                "timestamp": time.time(),
            }), 503

    @bp.route("/metrics", methods=["GET"])
    def metrics() -> Any:
        """!
        @brief Prometheus metrics endpoint.

        @details
        Returns metrics in Prometheus text exposition format.
        """
        return Response(
            _metrics.render(),
            mimetype="text/plain; version=0.0.4; charset=utf-8",
        )

    return bp
