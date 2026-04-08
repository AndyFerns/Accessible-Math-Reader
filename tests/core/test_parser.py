# ============================================================================
# tests/core/test_parser.py — MathParser unit tests
# ============================================================================
"""
Tests for accessible_math_reader.core.parser.MathParser

Covers:
  - LaTeX parsing (fractions, exponents, subscripts, roots, Greek, operators)
  - MathML parsing (mfrac, msup, msub, msqrt, mi, mn, mo)
  - Plaintext / Unicode parsing (a/b, x², √, Greek chars)
  - Format auto-detection
  - Edge cases & error handling (empty input, unclosed braces, etc.)
"""

import pytest

from accessible_math_reader.core.parser import MathParser, ParseError
from accessible_math_reader.core.semantic import NodeType


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def parser():
    return MathParser()


# ══════════════════════════════════════════════════════════════════════════
# FORMAT AUTO-DETECTION
# ══════════════════════════════════════════════════════════════════════════


class TestFormatDetection:
    """Verify _detect_format heuristics."""

    def test_detects_latex(self, parser):
        assert parser._detect_format(r"\frac{a}{b}") == "latex"

    def test_detects_mathml(self, parser):
        assert parser._detect_format("<math><mi>x</mi></math>") == "mathml"

    def test_detects_mathml_xml_decl(self, parser):
        assert parser._detect_format('<?xml version="1.0"?>') == "mathml"

    def test_detects_plaintext(self, parser):
        assert parser._detect_format("a + b = c") == "plaintext"

    def test_detects_unicode_as_plaintext(self, parser):
        assert parser._detect_format("x² + y²") == "plaintext"


# ══════════════════════════════════════════════════════════════════════════
# LaTeX PARSING
# ══════════════════════════════════════════════════════════════════════════


class TestLatexParsing:
    """Verify LaTeX → SemanticNode tree correctness."""

    def test_simple_identifier(self, parser):
        tree = parser.parse_latex("x")
        assert tree.node_type == NodeType.ROOT
        assert len(tree.children) == 1
        assert tree.children[0].node_type == NodeType.IDENTIFIER
        assert tree.children[0].content == "x"

    def test_number(self, parser):
        tree = parser.parse_latex("42")
        assert tree.children[0].node_type == NodeType.NUMBER
        assert tree.children[0].content == "42"

    def test_decimal_number(self, parser):
        tree = parser.parse_latex("3.14")
        assert tree.children[0].node_type == NodeType.NUMBER
        assert tree.children[0].content == "3.14"

    def test_fraction(self, parser):
        tree = parser.parse_latex(r"\frac{a}{b}")
        frac = tree.children[0]
        assert frac.node_type == NodeType.FRACTION
        assert len(frac.children) == 2  # numerator, denominator

    def test_fraction_numerator_content(self, parser):
        tree = parser.parse_latex(r"\frac{a}{b}")
        frac = tree.children[0]
        # Numerator is a GROUP containing IDENTIFIER "a"
        num = frac.children[0]
        assert num.node_type == NodeType.GROUP
        assert num.children[0].content == "a"

    def test_fraction_denominator_content(self, parser):
        tree = parser.parse_latex(r"\frac{a}{b}")
        frac = tree.children[0]
        denom = frac.children[1]
        assert denom.children[0].content == "b"

    def test_superscript(self, parser):
        tree = parser.parse_latex("x^2")
        sup = tree.children[0]
        assert sup.node_type == NodeType.SUPERSCRIPT
        # base = x, exponent = 2
        assert sup.children[0].content == "x"

    def test_superscript_braced(self, parser):
        tree = parser.parse_latex("x^{10}")
        sup = tree.children[0]
        assert sup.node_type == NodeType.SUPERSCRIPT
        # exponent group should contain "10"
        exp_group = sup.children[1]
        assert any(c.content == "10" for c in exp_group.walk_leaves())

    def test_subscript(self, parser):
        tree = parser.parse_latex("x_i")
        sub = tree.children[0]
        assert sub.node_type == NodeType.SUBSCRIPT

    def test_sqrt(self, parser):
        tree = parser.parse_latex(r"\sqrt{x}")
        sqrt = tree.children[0]
        assert sqrt.node_type == NodeType.SQRT

    def test_nth_root(self, parser):
        tree = parser.parse_latex(r"\sqrt[3]{x}")
        nroot = tree.children[0]
        assert nroot.node_type == NodeType.NROOT

    def test_greek_alpha(self, parser):
        tree = parser.parse_latex(r"\alpha")
        assert tree.children[0].node_type == NodeType.IDENTIFIER
        assert tree.children[0].content == "α"

    def test_greek_pi(self, parser):
        tree = parser.parse_latex(r"\pi")
        assert tree.children[0].content == "π"

    def test_operator_plus(self, parser):
        tree = parser.parse_latex("a+b")
        ops = [c for c in tree.children if c.node_type == NodeType.OPERATOR]
        assert len(ops) >= 1
        assert ops[0].content == "+"

    def test_relation_equals(self, parser):
        tree = parser.parse_latex("a=b")
        rels = [c for c in tree.children if c.node_type == NodeType.RELATION]
        assert len(rels) >= 1
        assert rels[0].content == "="

    def test_function_sin(self, parser):
        tree = parser.parse_latex(r"\sin")
        fn = tree.children[0]
        assert fn.node_type == NodeType.FUNCTION
        assert fn.content == "sin"

    def test_sum_symbol(self, parser):
        tree = parser.parse_latex(r"\sum")
        assert tree.children[0].node_type == NodeType.SUM

    def test_integral_symbol(self, parser):
        tree = parser.parse_latex(r"\int")
        assert tree.children[0].node_type == NodeType.INTEGRAL

    def test_infinity(self, parser):
        tree = parser.parse_latex(r"\infty")
        assert tree.children[0].content == "∞"

    def test_strips_dollar_signs(self, parser):
        tree = parser.parse_latex("$x$")
        assert tree.children[0].content == "x"

    def test_nested_fraction(self, parser):
        tree = parser.parse_latex(r"\frac{\frac{a}{b}}{c}")
        outer = tree.children[0]
        assert outer.node_type == NodeType.FRACTION
        inner_num = outer.children[0]
        # The numerator group should contain a nested FRACTION
        fracs = [n for n in inner_num.walk() if n.node_type == NodeType.FRACTION]
        assert len(fracs) >= 1


# ══════════════════════════════════════════════════════════════════════════
# MathML PARSING
# ══════════════════════════════════════════════════════════════════════════


class TestMathMLParsing:
    """Verify MathML → SemanticNode tree correctness."""

    def test_mi_identifier(self, parser):
        tree = parser.parse_mathml("<math><mi>x</mi></math>")
        idents = [n for n in tree.walk() if n.node_type == NodeType.IDENTIFIER]
        assert len(idents) >= 1
        assert idents[0].content == "x"

    def test_mn_number(self, parser):
        tree = parser.parse_mathml("<math><mn>42</mn></math>")
        nums = [n for n in tree.walk() if n.node_type == NodeType.NUMBER]
        assert nums[0].content == "42"

    def test_mo_operator(self, parser):
        tree = parser.parse_mathml("<math><mo>+</mo></math>")
        ops = [n for n in tree.walk() if n.node_type == NodeType.OPERATOR]
        assert len(ops) >= 1

    def test_mo_relation(self, parser):
        tree = parser.parse_mathml("<math><mo>=</mo></math>")
        rels = [n for n in tree.walk() if n.node_type == NodeType.RELATION]
        assert len(rels) >= 1

    def test_mfrac(self, parser):
        tree = parser.parse_mathml(
            "<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>"
        )
        fracs = [n for n in tree.walk() if n.node_type == NodeType.FRACTION]
        assert len(fracs) == 1

    def test_msup(self, parser):
        tree = parser.parse_mathml(
            "<math><msup><mi>x</mi><mn>2</mn></msup></math>"
        )
        sups = [n for n in tree.walk() if n.node_type == NodeType.SUPERSCRIPT]
        assert len(sups) == 1

    def test_msub(self, parser):
        tree = parser.parse_mathml(
            "<math><msub><mi>x</mi><mi>i</mi></msub></math>"
        )
        subs = [n for n in tree.walk() if n.node_type == NodeType.SUBSCRIPT]
        assert len(subs) == 1

    def test_msqrt(self, parser):
        tree = parser.parse_mathml(
            "<math><msqrt><mi>x</mi></msqrt></math>"
        )
        sqrts = [n for n in tree.walk() if n.node_type == NodeType.SQRT]
        assert len(sqrts) == 1

    def test_invalid_mathml_raises(self, parser):
        with pytest.raises(ParseError, match="Invalid MathML"):
            parser.parse_mathml("<math><unclosed>")


# ══════════════════════════════════════════════════════════════════════════
# PLAINTEXT / UNICODE PARSING
# ══════════════════════════════════════════════════════════════════════════


class TestPlaintextParsing:
    """Verify plaintext/Unicode → SemanticNode correctness."""

    def test_simple_addition(self, parser):
        tree = parser.parse_plaintext("a + b")
        leaves = list(tree.walk_leaves())
        contents = [l.content for l in leaves]
        assert "a" in contents
        assert "b" in contents

    def test_unicode_superscript(self, parser):
        tree = parser.parse_plaintext("x²")
        sups = [n for n in tree.walk() if n.node_type == NodeType.SUPERSCRIPT]
        assert len(sups) >= 1

    def test_unicode_subscript(self, parser):
        tree = parser.parse_plaintext("x₁")
        subs = [n for n in tree.walk() if n.node_type == NodeType.SUBSCRIPT]
        assert len(subs) >= 1

    def test_empty_raises(self, parser):
        with pytest.raises(ParseError):
            parser.parse_plaintext("")

    def test_whitespace_only_raises(self, parser):
        with pytest.raises(ParseError):
            parser.parse_plaintext("   ")


# ══════════════════════════════════════════════════════════════════════════
# EDGE CASES & ERROR HANDLING
# ══════════════════════════════════════════════════════════════════════════


class TestParserEdgeCases:
    """Cover tricky inputs that might crash or produce wrong trees."""

    def test_empty_string_raises(self, parser):
        with pytest.raises(ParseError, match="Empty input"):
            parser.parse("")

    def test_whitespace_only_raises(self, parser):
        with pytest.raises(ParseError):
            parser.parse("   ")

    def test_unclosed_brace_raises(self, parser):
        with pytest.raises(ParseError, match="Unclosed brace"):
            parser.parse_latex(r"\frac{a}{")

    def test_superscript_without_base_raises(self, parser):
        with pytest.raises(ParseError, match="Superscript without base"):
            parser.parse_latex("^2")

    def test_subscript_without_base_raises(self, parser):
        with pytest.raises(ParseError, match="Subscript without base"):
            parser.parse_latex("_i")

    def test_unknown_command_preserved(self, parser):
        """Unknown LaTeX commands should be kept as TEXT, not crash."""
        tree = parser.parse_latex(r"\unknowncmd")
        text_nodes = [n for n in tree.walk() if n.node_type == NodeType.TEXT]
        assert any("unknowncmd" in n.content for n in text_nodes)

    def test_very_long_expression_no_crash(self, parser):
        """Stress test — a 500-variable sum should not crash."""
        expr = " + ".join(f"x_{i}" for i in range(500))
        tree = parser.parse_latex(expr)
        assert tree.node_type == NodeType.ROOT

    def test_special_characters_no_crash(self, parser):
        """Characters outside standard math should not crash."""
        tree = parser.parse("!@#%&")
        assert tree is not None

    def test_injection_like_input(self, parser):
        """HTML/script-like input should not crash the parser."""
        tree = parser.parse("<script>alert('x')</script>")
        assert tree is not None
