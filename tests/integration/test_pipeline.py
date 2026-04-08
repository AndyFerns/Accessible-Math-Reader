# ============================================================================
# tests/integration/test_pipeline.py — End-to-end pipeline tests
# ============================================================================
"""
Integration tests that exercise the full conversion pipeline:
    Input → MathReader → parse → render (speech/braille) → [audio]

Verifies that all components work together without mocking
the core library (gTTS is still mocked to avoid network).
"""

import os
from unittest.mock import patch, MagicMock

import pytest

from accessible_math_reader.reader import MathReader
from accessible_math_reader.config import Config, SpeechConfig, SpeechStyle


@pytest.fixture()
def reader():
    return MathReader()


# ══════════════════════════════════════════════════════════════════════════
# FULL PIPELINE: LaTeX → speech + braille
# ══════════════════════════════════════════════════════════════════════════


class TestFullPipelineLatex:
    """End-to-end: LaTeX string → speech text & braille string."""

    def test_fraction_to_speech(self, reader):
        speech = reader.to_speech(r"\frac{a}{b}")
        assert isinstance(speech, str)
        assert len(speech) > 0
        assert "over" in speech.lower()

    def test_fraction_to_braille(self, reader):
        braille = reader.to_braille(r"\frac{a}{b}")
        assert isinstance(braille, str)
        assert len(braille) > 0
        # Braille should contain actual Braille Unicode characters
        assert any(0x2800 <= ord(c) <= 0x28FF for c in braille)

    def test_quadratic_to_speech(self, reader):
        speech = reader.to_speech(r"x^2 + 2x + 1 = 0")
        assert "power" in speech.lower() or "to the" in speech.lower()
        assert "plus" in speech.lower()
        assert "equals" in speech.lower()

    def test_sqrt_to_speech(self, reader):
        speech = reader.to_speech(r"\sqrt{x}")
        assert "root" in speech.lower()

    def test_greek_to_speech(self, reader):
        speech = reader.to_speech(r"\alpha + \beta")
        assert "alpha" in speech.lower()
        assert "beta" in speech.lower()

    def test_structure_returns_dict(self, reader):
        struct = reader.get_structure(r"\frac{a}{b}")
        assert isinstance(struct, dict)
        assert "type" in struct
        assert struct["type"] == "ROOT"

    def test_ssml_output(self, reader):
        ssml = reader.to_ssml(r"\frac{a}{b}")
        assert "<speak" in ssml
        assert "</speak>" in ssml


# ══════════════════════════════════════════════════════════════════════════
# FULL PIPELINE: Plaintext & Unicode
# ══════════════════════════════════════════════════════════════════════════


class TestFullPipelinePlaintext:
    """End-to-end for plaintext / Unicode copy-paste math."""

    def test_simple_addition(self, reader):
        speech = reader.to_speech("a + b")
        assert "plus" in speech.lower()

    def test_unicode_exponent(self, reader):
        speech = reader.to_speech("x²")
        assert "power" in speech.lower() or "to the" in speech.lower()

    def test_fraction_slash(self, reader):
        speech = reader.to_speech("a/b")
        assert isinstance(speech, str)
        assert len(speech) > 0


# ══════════════════════════════════════════════════════════════════════════
# FULL PIPELINE: Audio generation (mocked TTS)
# ══════════════════════════════════════════════════════════════════════════


class TestAudioPipeline:
    """Pipeline through to audio file creation (gTTS mocked)."""

    def test_audio_creates_file(self, reader, tmp_path):
        out = tmp_path / "output.mp3"
        fake_tts = MagicMock()
        fake_tts.return_value.save = lambda p: open(p, "wb").write(b"\x00" * 64)

        with patch("gtts.gTTS", fake_tts):
            reader.to_audio(r"\frac{a}{b}", str(out))
            assert out.exists()
            assert out.stat().st_size > 0

    def test_audio_file_extension(self, reader, tmp_path):
        out = tmp_path / "test.mp3"
        fake_tts = MagicMock()
        fake_tts.return_value.save = lambda p: open(p, "wb").write(b"\x00" * 64)

        with patch("gtts.gTTS", fake_tts):
            result_path = reader.to_audio("x + y", str(out))
            assert str(result_path).endswith(".mp3")


# ══════════════════════════════════════════════════════════════════════════
# VERBOSITY SWITCHING
# ══════════════════════════════════════════════════════════════════════════


class TestVerbositySwitching:
    """Verify that switching verbosity changes output."""

    def test_verbose_vs_concise(self):
        verbose_reader = MathReader(
            Config(speech=SpeechConfig(style=SpeechStyle.VERBOSE))
        )
        concise_reader = MathReader(
            Config(speech=SpeechConfig(style=SpeechStyle.CONCISE))
        )
        v = verbose_reader.to_speech(r"\frac{a}{b}")
        c = concise_reader.to_speech(r"\frac{a}{b}")
        # Verbose should be longer than concise
        assert len(v) > len(c)

    def test_set_verbosity_method(self):
        reader = MathReader()
        reader.set_verbosity("verbose")
        v = reader.to_speech(r"\frac{a}{b}")
        reader.set_verbosity("concise")
        c = reader.to_speech(r"\frac{a}{b}")
        assert len(v) > len(c)


# ══════════════════════════════════════════════════════════════════════════
# NAVIGATOR INTEGRATION
# ══════════════════════════════════════════════════════════════════════════


class TestNavigatorIntegration:
    """Verify get_navigator works end-to-end."""

    def test_navigator_from_latex(self, reader):
        nav = reader.get_navigator(r"\frac{a}{b}")
        assert nav.current is not None
        assert nav.enter()  # should be able to enter fraction

    def test_navigator_walk(self, reader):
        nav = reader.get_navigator(r"x^2 + y^2")
        path = nav.get_path()
        assert len(path) >= 1


# ══════════════════════════════════════════════════════════════════════════
# STABILITY — repeated calls
# ══════════════════════════════════════════════════════════════════════════


class TestStability:
    """Ensure determinism and no resource leaks over repeated calls."""

    def test_repeated_speech_deterministic(self, reader):
        results = [reader.to_speech(r"\frac{a}{b}") for _ in range(20)]
        assert len(set(results)) == 1

    def test_repeated_braille_deterministic(self, reader):
        results = [reader.to_braille(r"\frac{a}{b}") for _ in range(20)]
        assert len(set(results)) == 1

    def test_many_different_expressions(self, reader):
        """No crash over many varied inputs."""
        expressions = [
            r"\frac{a}{b}", r"x^2", r"\sqrt{x}", r"\alpha",
            "a + b", "x²", "(a+b)/(c-d)", r"\int x dx",
            r"\sum_{i=1}^{n} x_i", r"\frac{\sqrt{a}}{b^2}",
        ]
        for expr in expressions:
            speech = reader.to_speech(expr)
            braille = reader.to_braille(expr)
            assert isinstance(speech, str)
            assert isinstance(braille, str)
