"""!
@file server.py
@brief Unified WSGI entry point for production deployment.

@details
Creates a Flask application that includes both the original web UI
(from ``app.py``) and the REST API Blueprint.  This is the entry
point for Gunicorn / Docker deployments.

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
@version 0.2.0
"""

from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)


def create_app():
    """!
    @brief Application factory for the unified AMR server.

    @details
    Creates a Flask app that mounts:
      - The original web UI at ``/`` (from the root ``app.py``)
      - The REST API at ``/api/v1/*``
      - Infrastructure routes (``/health``, ``/readiness``, ``/metrics``)

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

    # ── Register the original web UI routes ───────────────────
    # Import the original app module and replicate its routes
    # so that the web UI continues to work identically.
    sys.path.insert(0, project_root)

    from src.latex_parser import parse_math_input, latex_to_braille_simple
    from src.speech_converter import text_to_speech
    from src.braille_converter import math_to_braille

    # Ensure the audio directory exists
    audio_dir = os.path.join(static_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    from flask import render_template, request, send_from_directory

    @app.route("/")
    def index():
        return render_template("index.html", input_text=None, readable_text=None)

    @app.route("/convert", methods=["POST"])
    def convert():
        math_input = request.form.get("math_input", "")
        readable_text = parse_math_input(math_input)
        simple_math_text = latex_to_braille_simple(math_input)
        braille_text = math_to_braille(simple_math_text)
        audio_path = text_to_speech(readable_text)
        audio_file = os.path.basename(audio_path)
        return render_template(
            "index.html",
            input_text=math_input,
            readable_text=readable_text,
            audio_file=audio_file,
            braille_text=braille_text,
        )

    @app.route("/audio/<path:filename>")
    def serve_audio(filename):
        return send_from_directory(audio_dir, filename)

    # ── Register the REST API Blueprint ───────────────────────
    from accessible_math_reader.api import create_api_blueprint
    app.register_blueprint(create_api_blueprint())

    # ── Request size limit ────────────────────────────────────
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
