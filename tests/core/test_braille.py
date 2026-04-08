# ============================================================================
# tests/core/test_braille.py — Nemeth Braille converter tests
# ============================================================================
"""
Tests for accessible_math_reader.braille.nemeth.NemethConverter

Covers:
  - Digit rendering with numeric indicator
  - Letter rendering (lowercase, uppercase, Greek)
  - Operator and relation symbols
  - Structural elements (fractions, superscripts, subscripts, roots)
  - Determinism — same input always yields same output
"""

import pytest

from accessible_math_reader.core.parser import MathParser
from accessible_math_reader.braille.nemeth import NemethConverter
from accessible_math_reader.core.semantic import SemanticNode, NodeType


@pytest.fixture()
def parser():
    return MathParser()


@pytest.fixture()
def nemeth():
    return NemethConverter()


# ══════════════════════════════════════════════════════════════════════════
# DIGIT RENDERING
# ══════════════════════════════════════════════════════════════════════════


class TestNemethDigits:
    """Verify numeric indicator + digit cells."""

    def test_single_digit(self, nemeth):
        node = SemanticNode(NodeType.NUMBER, content="1")
        result = nemeth.render(node)
        assert result.startswith(NemethConverter.NUMERIC_INDICATOR)
        assert NemethConverter.DIGITS["1"] in result

    def test_multi_digit(self, nemeth):
        node = SemanticNode(NodeType.NUMBER, content="42")
        result = nemeth.render(node)
        assert NemethConverter.DIGITS["4"] in result
        assert NemethConverter.DIGITS["2"] in result

    def test_decimal_number(self, nemeth):
        node = SemanticNode(NodeType.NUMBER, content="3.14")
        result = nemeth.render(node)
        assert "⠨" in result  # Nemeth decimal point


# ══════════════════════════════════════════════════════════════════════════
# LETTER RENDERING
# ══════════════════════════════════════════════════════════════════════════


class TestNemethLetters:
    """Verify letter indicator and conversion."""

    def test_lowercase_letter(self, nemeth):
        node = SemanticNode(NodeType.IDENTIFIER, content="x")
        result = nemeth.render(node)
        assert result == NemethConverter.LETTERS["x"]

    def test_uppercase_letter(self, nemeth):
        node = SemanticNode(NodeType.IDENTIFIER, content="A")
        result = nemeth.render(node)
        assert result.startswith("⠠")  # capital indicator

    def test_greek_alpha(self, nemeth):
        node = SemanticNode(NodeType.IDENTIFIER, content="α")
        result = nemeth.render(node)
        assert result == NemethConverter.GREEK["α"]

    def test_infinity(self, nemeth):
        node = SemanticNode(NodeType.IDENTIFIER, content="∞")
        result = nemeth.render(node)
        assert result == "⠠⠿"


# ══════════════════════════════════════════════════════════════════════════
# OPERATORS & RELATIONS
# ══════════════════════════════════════════════════════════════════════════


class TestNemethOperators:

    def test_plus(self, nemeth):
        node = SemanticNode(NodeType.OPERATOR, content="+")
        assert nemeth.render(node) == NemethConverter.OPERATORS["+"]

    def test_minus(self, nemeth):
        node = SemanticNode(NodeType.OPERATOR, content="-")
        assert nemeth.render(node) == NemethConverter.OPERATORS["-"]

    def test_equals(self, nemeth):
        node = SemanticNode(NodeType.RELATION, content="=")
        assert nemeth.render(node) == NemethConverter.RELATIONS["="]


# ══════════════════════════════════════════════════════════════════════════
# STRUCTURAL ELEMENTS
# ══════════════════════════════════════════════════════════════════════════


class TestNemethStructures:
    """Fraction, superscript, subscript, sqrt."""

    def test_fraction_structure(self, parser, nemeth):
        tree = parser.parse(r"\frac{a}{b}")
        result = nemeth.render(tree)
        # Must contain fraction open, fraction line, and fraction close
        assert NemethConverter.FRACTION_OPEN in result
        assert NemethConverter.FRACTION_LINE in result
        assert NemethConverter.FRACTION_CLOSE in result

    def test_fraction_contains_operands(self, parser, nemeth):
        tree = parser.parse(r"\frac{a}{b}")
        result = nemeth.render(tree)
        assert NemethConverter.LETTERS["a"] in result
        assert NemethConverter.LETTERS["b"] in result

    def test_superscript_indicator(self, parser, nemeth):
        tree = parser.parse("x^2")
        result = nemeth.render(tree)
        assert NemethConverter.SUPERSCRIPT_IND in result

    def test_subscript_indicator(self, parser, nemeth):
        tree = parser.parse("x_i")
        result = nemeth.render(tree)
        assert NemethConverter.SUBSCRIPT_IND in result

    def test_sqrt_open_close(self, parser, nemeth):
        tree = parser.parse(r"\sqrt{x}")
        result = nemeth.render(tree)
        assert NemethConverter.SQRT_OPEN in result
        assert NemethConverter.SQRT_CLOSE in result


# ══════════════════════════════════════════════════════════════════════════
# DETERMINISM
# ══════════════════════════════════════════════════════════════════════════


class TestNemethDeterminism:
    """Same input must always produce the same Braille output."""

    def test_deterministic_fraction(self, parser, nemeth):
        results = set()
        for _ in range(10):
            tree = parser.parse(r"\frac{1}{2}")
            results.add(nemeth.render(tree))
        assert len(results) == 1, f"Non-deterministic output: {results}"

    def test_deterministic_complex(self, parser, nemeth):
        expr = r"\frac{\sqrt{a^2+b^2}}{c}"
        results = set()
        for _ in range(10):
            tree = parser.parse(expr)
            results.add(nemeth.render(tree))
        assert len(results) == 1
