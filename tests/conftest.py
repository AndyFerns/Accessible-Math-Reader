# ============================================================================
# conftest.py — Shared pytest fixtures for Accessible Math Reader tests
# ============================================================================
"""
Root conftest providing:
  - Flask test client (app_client)
  - Server factory test client (server_client)
  - Shared MathReader instance
  - MathParser instance
  - Temporary directories for audio output
  - Sample test data constants
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures: Core library objects
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def math_reader():
    """Shared MathReader — created once per test session."""
    from accessible_math_reader.reader import MathReader

    return MathReader()


@pytest.fixture(scope="session")
def math_parser():
    """Shared MathParser — created once per test session."""
    from accessible_math_reader.core.parser import MathParser

    return MathParser()


# ---------------------------------------------------------------------------
# Fixtures: Flask test clients
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_client(tmp_path):
    """
    Flask test client for the development entry point (app.py).
    Patches AUDIO_DIR to a temp dir so tests never pollute static/audio.
    """
    import app as app_module

    app_module.AUDIO_DIR = str(tmp_path)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture()
def server_client():
    """
    Flask test client for the production entry point (server.py → create_app).

    Because create_app imports the API blueprint (which pulls in
    observability, auth middleware, etc.), we mock the external deps
    that are expensive or require network to keep the suite fast.
    """
    from accessible_math_reader.server import create_app

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Fixtures: Temporary directories and files
# ---------------------------------------------------------------------------


@pytest.fixture()
def audio_dir(tmp_path):
    """Temporary directory for audio file output."""
    d = tmp_path / "audio"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Fixtures: Mock TTS backend (avoids network during test)
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_gtts():
    """
    Patch gTTS so that to_audio calls create a tiny valid file
    instead of hitting the Google TTS API.
    """
    fake_tts = MagicMock()
    fake_tts.return_value.save = lambda path: _write_fake_mp3(path)
    with patch("gtts.gTTS", fake_tts):
        yield fake_tts


def _write_fake_mp3(path):
    """Write a minimal file that acts as a placeholder MP3."""
    with open(path, "wb") as f:
        # 4-byte header that starts with the MP3 sync word (0xFFE0)
        # Not a real MP3 frame but enough for file-existence assertions.
        f.write(b"\xff\xe0\x00\x00" + b"\x00" * 128)


# ---------------------------------------------------------------------------
# Constants: sample expressions used across test modules
# ---------------------------------------------------------------------------

LATEX_FRACTION = r"\frac{a}{b}"
LATEX_QUADRATIC = r"x^2 + 2x + 1 = 0"
LATEX_SQRT = r"\sqrt{x^2 + y^2}"
LATEX_NESTED = r"\frac{\sqrt{a^2 + b^2}}{c}"
LATEX_INTEGRAL = r"\int_{0}^{1} x^2 dx"
LATEX_GREEK = r"\alpha + \beta = \gamma"

MATHML_FRACTION = "<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>"
MATHML_SUPERSCRIPT = "<math><msup><mi>x</mi><mn>2</mn></msup></math>"

PLAINTEXT_SIMPLE = "a + b = c"
PLAINTEXT_FRACTION = "(a+b)/(c-d)"
PLAINTEXT_UNICODE_EXP = "x² + y²"
PLAINTEXT_UNICODE_GREEK = "α + β = γ"
