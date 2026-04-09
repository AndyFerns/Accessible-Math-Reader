"""
app.py — Flask Web Interface for Accessible Math Reader
========================================================

Thin Flask controller that delegates all math conversion logic to the
``accessible_math_reader`` package via its high-level ``MathReader`` API.

Routes:
    GET  /                  - Render the main web UI
    POST /convert           - Convert a math expression to speech, braille, & audio
    GET  /audio/<filename>  - Serve generated audio files from static/audio/

BREAKING CHANGE (v0.5.1):
    This file no longer imports from the legacy ``src/`` directory.
    All business logic now flows through ``accessible_math_reader.reader.MathReader``.

Authors: Accessible Math Reader Contributors
Version: 0.5.2
"""

import logging
import os
import uuid

from flask import Flask, render_template, request, send_from_directory

# ---------------------------------------------------------------------------
# Import the unified MathReader from the main package.
# This replaces the legacy imports:
#   from src.latex_parser import parse_math_input, latex_to_braille_simple
#   from src.speech_converter import text_to_speech
#   from src.braille_converter import math_to_braille
# ---------------------------------------------------------------------------
from accessible_math_reader.reader import MathReader

# ---------------------------------------------------------------------------
# Application Setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Shared MathReader instance — initialised once, reused across requests.
reader = MathReader()

# Ensure the static/audio directory exists for TTS output files.
AUDIO_DIR = os.path.join(app.root_path, "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the main page with empty inputs on initial load."""
    return render_template("index.html", input_text=None, readable_text=None)


@app.route("/convert", methods=["POST"])
def convert():
    """
    Accept a math expression from the form, convert it to speech text,
    Braille, and an audio file, then re-render the page with results.

    Conversion pipeline (all via MathReader):
        1. to_speech()  → readable English text  (e.g. "a divided by b")
        2. to_braille() → Nemeth Braille string   (e.g. "⠹⠁⠌⠃⠼")
        3. to_audio()   → MP3 file in static/audio/

    Audio files are given UUID-based names to prevent overwrite collisions
    when multiple users submit concurrently.
    """
    math_input = request.form.get("math_input", "")

    try:
        # 1. Generate readable English text for speech output
        readable_text = reader.to_speech(math_input)

        # 2. Generate Nemeth Braille text
        braille_text = reader.to_braille(math_input, notation="nemeth")

        # 3. Generate audio file with a unique filename to avoid collisions
        audio_filename = f"{uuid.uuid4().hex}.mp3"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        reader.to_audio(math_input, audio_path)

    except Exception:
        # Log the full traceback for debugging, but show a friendly message
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
    return send_from_directory(AUDIO_DIR, filename)


# ---------------------------------------------------------------------------
# Development Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)