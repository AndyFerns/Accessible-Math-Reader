# ============================================================================
# tests/core/test_speech.py — Speech rendering & TTS engine tests
# ============================================================================
"""
Tests for:
  - accessible_math_reader.speech.rules.SpeechRenderer
  - accessible_math_reader.speech.rules.SpeechRuleSet
  - accessible_math_reader.speech.engine.SpeechEngine

Covers:
  - Correct speech text for fractions, exponents, subscripts, roots
  - Verbosity levels (verbose, concise, superbrief)
  - Operator / relation / identifier name lookups
  - SSML generation
  - Math-specific SSML with pauses
"""

import pytest
from unittest.mock import patch, MagicMock

from accessible_math_reader.core.parser import MathParser
from accessible_math_reader.speech.rules import (
    SpeechRenderer,
    SpeechRuleSet,
    VerbosityLevel,
)
from accessible_math_reader.speech.engine import SpeechEngine
from accessible_math_reader.config import Config, SpeechConfig, SpeechStyle


@pytest.fixture()
def parser():
    return MathParser()


@pytest.fixture()
def verbose_renderer():
    config = Config(speech=SpeechConfig(style=SpeechStyle.VERBOSE))
    return SpeechRenderer(config)


@pytest.fixture()
def concise_renderer():
    config = Config(speech=SpeechConfig(style=SpeechStyle.CONCISE))
    return SpeechRenderer(config)


# ══════════════════════════════════════════════════════════════════════════
# SpeechRuleSet lookups
# ══════════════════════════════════════════════════════════════════════════


class TestSpeechRuleSet:
    """Verify rule-set phrase/name lookups."""

    def test_fraction_start_verbose(self):
        rules = SpeechRuleSet()
        assert rules.get_phrase("fraction_start", VerbosityLevel.VERBOSE) == "start fraction"

    def test_fraction_start_concise(self):
        rules = SpeechRuleSet()
        assert rules.get_phrase("fraction_start", VerbosityLevel.CONCISE) == ""

    def test_operator_plus(self):
        rules = SpeechRuleSet()
        assert rules.get_operator_name("+") == "plus"

    def test_operator_divide(self):
        rules = SpeechRuleSet()
        assert rules.get_operator_name("÷") == "divided by"

    def test_relation_equals(self):
        rules = SpeechRuleSet()
        assert rules.get_relation_name("=") == "equals"

    def test_relation_leq(self):
        rules = SpeechRuleSet()
        assert rules.get_relation_name("≤") == "less than or equal to"

    def test_identifier_pi(self):
        rules = SpeechRuleSet()
        assert rules.get_identifier_name("π") == "pi"

    def test_identifier_alpha(self):
        rules = SpeechRuleSet()
        assert rules.get_identifier_name("α") == "alpha"

    def test_unknown_operator_returns_itself(self):
        rules = SpeechRuleSet()
        assert rules.get_operator_name("⊕") == "⊕"


# ══════════════════════════════════════════════════════════════════════════
# SpeechRenderer — verbose mode
# ══════════════════════════════════════════════════════════════════════════


class TestSpeechRendererVerbose:
    """Verbose speech output correctness."""

    def test_fraction(self, parser, verbose_renderer):
        tree = parser.parse(r"\frac{a}{b}")
        text = verbose_renderer.render(tree)
        assert "start fraction" in text
        assert "over" in text
        assert "end fraction" in text

    def test_fraction_contains_variables(self, parser, verbose_renderer):
        tree = parser.parse(r"\frac{a}{b}")
        text = verbose_renderer.render(tree)
        assert "a" in text
        assert "b" in text

    def test_superscript(self, parser, verbose_renderer):
        tree = parser.parse("x^2")
        text = verbose_renderer.render(tree)
        assert "to the power of" in text

    def test_subscript(self, parser, verbose_renderer):
        tree = parser.parse("x_i")
        text = verbose_renderer.render(tree)
        assert "subscript" in text

    def test_sqrt(self, parser, verbose_renderer):
        tree = parser.parse(r"\sqrt{x}")
        text = verbose_renderer.render(tree)
        assert "square root of" in text

    def test_operator_plus_spelled(self, parser, verbose_renderer):
        tree = parser.parse("a+b")
        text = verbose_renderer.render(tree)
        assert "plus" in text

    def test_relation_equals_spelled(self, parser, verbose_renderer):
        tree = parser.parse("a=b")
        text = verbose_renderer.render(tree)
        assert "equals" in text

    def test_greek_letter(self, parser, verbose_renderer):
        tree = parser.parse(r"\alpha")
        text = verbose_renderer.render(tree)
        assert "alpha" in text


# ══════════════════════════════════════════════════════════════════════════
# SpeechRenderer — concise mode
# ══════════════════════════════════════════════════════════════════════════


class TestSpeechRendererConcise:
    """Concise mode should omit structural announcements."""

    def test_fraction_no_start_end(self, parser, concise_renderer):
        tree = parser.parse(r"\frac{a}{b}")
        text = concise_renderer.render(tree)
        assert "start fraction" not in text
        assert "end fraction" not in text
        # But "over" should still be present
        assert "over" in text


# ══════════════════════════════════════════════════════════════════════════
# SpeechEngine — SSML generation (no network)
# ══════════════════════════════════════════════════════════════════════════


class TestSpeechEngineSSML:
    """Test SSML markup generation (unit only, no TTS call)."""

    def test_to_ssml_structure(self):
        engine = SpeechEngine()
        ssml = engine.to_ssml("a over b")
        assert "<speak" in ssml
        assert "<prosody" in ssml
        assert "a over b" in ssml
        assert "</speak>" in ssml

    def test_to_ssml_rate(self):
        engine = SpeechEngine()
        ssml = engine.to_ssml("hello", rate=1.5)
        assert '150%' in ssml

    def test_to_math_ssml_has_breaks(self):
        engine = SpeechEngine()
        ssml = engine.to_math_ssml("start fraction a over b end fraction")
        assert "break" in ssml

    def test_ssml_escapes_entities(self):
        engine = SpeechEngine()
        ssml = engine.to_ssml("a < b & c > d")
        assert "&lt;" in ssml
        assert "&amp;" in ssml
        assert "&gt;" in ssml

    def test_synthesize_with_mocked_gtts(self, tmp_path):
        """Full synthesize path with mocked gTTS backend."""
        fake_tts_instance = MagicMock()
        fake_tts_class = MagicMock(return_value=fake_tts_instance)

        with patch("gtts.gTTS", fake_tts_class):
            engine = SpeechEngine()
            out = tmp_path / "test.mp3"
            engine.synthesize("hello world", str(out))
            fake_tts_class.assert_called_once()
            fake_tts_instance.save.assert_called_once()
