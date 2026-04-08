# ============================================================================
# tests/api/test_web_routes.py — Flask web UI route tests
# ============================================================================
"""
Tests for app.py routes: GET /, POST /convert, GET /audio/<file>

Uses Flask test client — no real server is started.
gTTS is mocked to avoid network calls during /convert.
"""

import os
from unittest.mock import patch, MagicMock

import pytest


# ── Helper to create the test client with mocked audio ────────────────────


@pytest.fixture()
def client(tmp_path):
    """
    Build a Flask test client from app.py with:
      - AUDIO_DIR pointed at a temp directory
      - gTTS mocked to create a small fake .mp3 file
    """
    # Patch gTTS before importing app (which creates a MathReader at import-time)
    fake_tts_instance = MagicMock()

    def fake_save(path):
        with open(path, "wb") as f:
            f.write(b"\xff\xe0" + b"\x00" * 64)

    fake_tts_instance.save = fake_save
    fake_tts_class = MagicMock(return_value=fake_tts_instance)

    with patch("gtts.gTTS", fake_tts_class):
        import app as app_module

        app_module.AUDIO_DIR = str(tmp_path)
        app_module.app.config["TESTING"] = True
        with app_module.app.test_client() as c:
            yield c, tmp_path


# ══════════════════════════════════════════════════════════════════════════
# GET /
# ══════════════════════════════════════════════════════════════════════════


class TestIndexRoute:
    """Verify the home page loads correctly."""

    def test_returns_200(self, client):
        c, _ = client
        resp = c.get("/")
        assert resp.status_code == 200

    def test_content_type_html(self, client):
        c, _ = client
        resp = c.get("/")
        assert "text/html" in resp.content_type

    def test_contains_form(self, client):
        c, _ = client
        resp = c.get("/")
        data = resp.data.decode()
        assert "<form" in data.lower()

    def test_contains_convert_action(self, client):
        c, _ = client
        resp = c.get("/")
        data = resp.data.decode()
        assert "/convert" in data


# ══════════════════════════════════════════════════════════════════════════
# POST /convert
# ══════════════════════════════════════════════════════════════════════════


class TestConvertRoute:
    """Verify conversion produces correct responses."""

    def test_valid_latex_returns_200(self, client):
        c, _ = client
        resp = c.post("/convert", data={"math_input": r"\frac{a}{b}"})
        assert resp.status_code == 200

    def test_valid_latex_shows_speech(self, client):
        c, _ = client
        resp = c.post("/convert", data={"math_input": r"\frac{a}{b}"})
        body = resp.data.decode()
        # The response HTML should contain the readable speech text
        assert "fraction" in body.lower() or "over" in body.lower()

    def test_valid_latex_shows_braille(self, client):
        c, _ = client
        resp = c.post("/convert", data={"math_input": r"\frac{a}{b}"})
        body = resp.data.decode()
        # Braille output uses special Unicode dots
        assert "⠹" in body or "braille" in body.lower()

    def test_valid_latex_creates_audio_file(self, client):
        c, tmp = client
        c.post("/convert", data={"math_input": r"\frac{a}{b}"})
        # An mp3 file should exist in the tmp audio dir
        mp3_files = [f for f in os.listdir(str(tmp)) if f.endswith(".mp3")]
        assert len(mp3_files) >= 1

    def test_unique_audio_filenames(self, client):
        c, tmp = client
        c.post("/convert", data={"math_input": "x"})
        c.post("/convert", data={"math_input": "y"})
        mp3_files = [f for f in os.listdir(str(tmp)) if f.endswith(".mp3")]
        assert len(mp3_files) >= 2
        # All filenames should be unique (UUID-based)
        assert len(set(mp3_files)) == len(mp3_files)

    def test_empty_input_returns_200_with_error(self, client):
        """Empty string should not crash; should show an error message."""
        c, _ = client
        resp = c.post("/convert", data={"math_input": ""})
        assert resp.status_code == 200
        body = resp.data.decode()
        assert "could not convert" in body.lower() or "error" in body.lower()

    def test_missing_field_returns_200(self, client):
        c, _ = client
        resp = c.post("/convert", data={})
        assert resp.status_code == 200

    def test_plaintext_input(self, client):
        c, _ = client
        resp = c.post("/convert", data={"math_input": "a + b = c"})
        assert resp.status_code == 200
        body = resp.data.decode()
        assert "plus" in body.lower()

    def test_unicode_input(self, client):
        c, _ = client
        resp = c.post("/convert", data={"math_input": "x² + y²"})
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════════════════
# GET /audio/<filename>
# ══════════════════════════════════════════════════════════════════════════


class TestAudioRoute:
    """Verify audio file serving."""

    def test_existing_file_returns_200(self, client):
        c, tmp = client
        # Create a fake audio file in the tmp dir
        fake_path = os.path.join(str(tmp), "test.mp3")
        with open(fake_path, "wb") as f:
            f.write(b"\xff\xe0" + b"\x00" * 64)

        resp = c.get("/audio/test.mp3")
        assert resp.status_code == 200

    def test_nonexistent_file_returns_404(self, client):
        c, _ = client
        resp = c.get("/audio/nonexistent.mp3")
        assert resp.status_code == 404

    def test_path_traversal_blocked(self, client):
        """Attempting directory traversal should not leak files."""
        c, _ = client
        resp = c.get("/audio/../../../etc/passwd")
        assert resp.status_code in (400, 403, 404)
