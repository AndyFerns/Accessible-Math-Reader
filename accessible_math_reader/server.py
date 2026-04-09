"""!
@file server.py
@brief Unified WSGI entry point for production deployment.

@details
Creates a Flask application that includes both the web UI routes and
the REST API Blueprint.  This is the entry point for Gunicorn / Docker
deployments.

All conversion logic is delegated to ``accessible_math_reader.reader.MathReader``.
The legacy ``src/`` directory is no longer used (removed in v0.5.1).

Start with Gunicorn:
@code{.bash}
gunicorn "accessible_math_reader.server:create_app()" -b 0.0.0.0:8000
@endcode

Or run directly:
@code{.bash}
python -m accessible_math_reader.server
@endcode

Environment variables:
  AMR_LOG_FORMAT, AMR_LOG_LEVEL  — logging configuration
  AMR_METRICS                    — enable Prometheus metrics
  AMR_ENABLE_AUTH                — enable API key auth
  AMR_ENABLE_RATE_LIMIT          — enable rate limiting

@author Accessible Math Reader Contributors
@version 0.5.2
"""

from __future__ import annotations

import logging
import os
import uuid

logger = logging.getLogger(__name__)


def create_app():
    """!
    @brief Application factory for the unified AMR server.

    @details
    Creates a Flask app that mounts:
      - The web UI at ``/`` (form-based conversion)
      - The REST API at ``/api/v1/*``
      - Infrastructure routes (``/health``, ``/readiness``, ``/metrics``)

    All math conversion is handled by ``MathReader`` from the
    ``accessible_math_reader`` package — no legacy ``src/`` imports.

    @return Configured Flask application
    """
    # Configure observability first
    from accessible_math_reader.observability import setup_logging
    setup_logging()

    from flask import Flask

    # Build app with correct template/static paths
    # (relative to the project root, not this package)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(project_root, "templates")
    static_dir = os.path.join(project_root, "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )

    # ── Shared MathReader instance ────────────────────────────────
    # Replaces the legacy imports:
    #   from src.latex_parser import parse_math_input, latex_to_braille_simple
    #   from src.speech_converter import text_to_speech
    #   from src.braille_converter import math_to_braille
    from accessible_math_reader.reader import MathReader
    reader = MathReader()

    # Ensure the audio directory exists
    audio_dir = os.path.join(static_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    from flask import render_template, request, send_from_directory

    # ── Web UI routes ─────────────────────────────────────────────

    @app.route("/")
    def index():
        """Render the main page with empty inputs on initial load."""
        return render_template("index.html", input_text=None, readable_text=None)

    @app.route("/convert", methods=["POST"])
    def convert():
        """
        Convert math input via MathReader and re-render the page.

        Pipeline:
            1. reader.to_speech()  → readable English text
            2. reader.to_braille() → Nemeth Braille string
            3. reader.to_audio()   → MP3 file (UUID-named to avoid collisions)
        """
        math_input = request.form.get("math_input", "")

        try:
            readable_text = reader.to_speech(math_input)
            braille_text = reader.to_braille(math_input, notation="nemeth")

            # UUID filename prevents concurrent request collisions
            audio_filename = f"{uuid.uuid4().hex}.mp3"
            audio_path = os.path.join(audio_dir, audio_filename)
            reader.to_audio(math_input, audio_path)
        except Exception:
            logger.exception("Conversion failed for input: %s", math_input)
            return render_template(
                "index.html",
                input_text=math_input,
                readable_text=None,
                error_message="Could not convert the expression. Please check your input and try again.",
            )

        return render_template(
            "index.html",
            input_text=math_input,
            readable_text=readable_text,
            audio_file=audio_filename,
            braille_text=braille_text,
        )

    @app.route("/audio/<path:filename>")
    def serve_audio(filename):
        """Serve generated audio files from the static/audio directory."""
        return send_from_directory(audio_dir, filename)

    # ── Register the REST API Blueprint ───────────────────────────
    from accessible_math_reader.api import create_api_blueprint
    app.register_blueprint(create_api_blueprint())

    # ── Request size limit ────────────────────────────────────────
    max_size = int(os.environ.get("AMR_MAX_REQUEST_SIZE", 1_048_576))  # 1 MB
    app.config["MAX_CONTENT_LENGTH"] = max_size

    logger.info(
        "AMR server created (max_request_size=%d, templates=%s)",
        max_size, template_dir,
    )
    return app


# ---------------------------------------------------------------------------
# Direct invocation for development
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("AMR_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
