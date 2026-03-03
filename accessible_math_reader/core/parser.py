"""!
@file core/parser.py
@brief Math expression parser for LaTeX, MathML, and plaintext input.

@details
Converts LaTeX, MathML, and plaintext/Unicode math strings into a
semantic AST representation. Supports common mathematical constructs
including fractions, exponents, subscripts, Greek letters, operators,
and standard copy-paste formats with Unicode math symbols.

The parser auto-detects the input format using the following heuristics:
  1. If the input starts with '<math' or '<?xml', it is parsed as MathML.
  2. If the input contains LaTeX commands (backslash followed by letters),
     it is parsed as LaTeX.
  3. Otherwise, it is parsed as plaintext/Unicode math.

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Optional

from accessible_math_reader.core.semantic import SemanticNode, NodeType


class ParseError(Exception):
    """!
    @brief Exception raised when parsing fails.
    
    @param message Error description
    @param position Character position where error occurred (if known)
    @param source Original input string
    """
    
    def __init__(
        self, 
        message: str, 
        position: Optional[int] = None,
        source: Optional[str] = None
    ) -> None:
        self.message = message
        self.position = position
        self.source = source
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format error message with context."""
        msg = self.message
        if self.position is not None and self.source:
            # Show context around the error
            start = max(0, self.position - 10)
            end = min(len(self.source), self.position + 10)
            context = self.source[start:end]
            pointer = " " * (self.position - start) + "^"
            msg += f"\n  Context: ...{context}...\n           {pointer}"
        return msg


class MathParser:
    """!
    @brief Parser for converting LaTeX/MathML/plaintext to semantic representation.
    
    @details
    Provides a unified interface for parsing mathematical notation
    into a format-agnostic semantic tree. Supports three input formats:
      - LaTeX  (e.g., \\frac{a}{b})
      - MathML (e.g., <math><mfrac>...</mfrac></math>)
      - Plaintext / Unicode math (e.g., (a+b)/(c-d), x², √x, π)
    
    @section parser_example Example Usage
    @code{.py}
    parser = MathParser()
    
    # Parse LaTeX (auto-detected)
    tree = parser.parse(r"\\frac{a}{b}")
    
    # Parse MathML (auto-detected)
    tree = parser.parse("<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>")
    
    # Parse plaintext / copy-paste math (auto-detected)
    tree = parser.parse("(a+b)/(c-d)")
    tree = parser.parse("x² + y² = z²")
    tree = parser.parse("√(a² + b²)")
    
    # Force a specific format
    tree = parser.parse_latex(r"\\frac{a}{b}")
    tree = parser.parse_mathml("<math>...</math>")
    tree = parser.parse_plaintext("a/b + c")
    @endcode
    """
    
    # Greek letter mappings
    GREEK_LETTERS = {
        "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
        "epsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ",
        "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ",
        "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
        "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ",
        "chi": "χ", "psi": "ψ", "omega": "ω",
        # Uppercase
        "Alpha": "Α", "Beta": "Β", "Gamma": "Γ", "Delta": "Δ",
        "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ", "Pi": "Π",
        "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
    }
    
    # Operator mappings
    OPERATORS = {
        "+": "+", "-": "-", "*": "×", "/": "÷",
        "\\times": "×", "\\cdot": "·", "\\div": "÷",
        "\\pm": "±", "\\mp": "∓",
    }
    
    # Relation mappings
    RELATIONS = {
        "=": "=", "<": "<", ">": ">",
        "\\leq": "≤", "\\geq": "≥", "\\neq": "≠",
        "\\approx": "≈", "\\equiv": "≡",
        "\\le": "≤", "\\ge": "≥", "\\ne": "≠",
    }
    
    # ── Unicode superscript / subscript digit mappings ──────────────────
    # Used by parse_plaintext() to convert Unicode super/subscript digits
    # back to their numeric values for semantic tree construction.
    UNICODE_SUPERSCRIPT_MAP: dict[str, str] = {
        "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
        "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
        "⁺": "+", "⁻": "-", "⁼": "=", "⁽": "(", "⁾": ")",
        "ⁿ": "n", "ⁱ": "i",
    }

    UNICODE_SUBSCRIPT_MAP: dict[str, str] = {
        "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
        "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
        "₊": "+", "₋": "-", "₌": "=", "₍": "(", "₎": ")",
        "ₐ": "a", "ₑ": "e", "ₒ": "o", "ₓ": "x", "ₙ": "n",
        "ᵢ": "i", "ⱼ": "j", "ₖ": "k",
    }

    # Unicode symbol → canonical character used by the plaintext tokenizer.
    UNICODE_SYMBOL_MAP: dict[str, str] = {
        # Operators
        "×": "*", "·": "*", "⋅": "*", "÷": "/",
        "±": "±", "∓": "∓",
        # Relations
        "≤": "<=", "≥": ">=", "≠": "!=", "≈": "≈", "≡": "≡",
        # Greek letters (Unicode char → name for speech)
        "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta",
        "ε": "epsilon", "ζ": "zeta", "η": "eta", "θ": "theta",
        "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu",
        "ν": "nu", "ξ": "xi", "π": "pi", "ρ": "rho",
        "σ": "sigma", "τ": "tau", "υ": "upsilon", "φ": "phi",
        "χ": "chi", "ψ": "psi", "ω": "omega",
        "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda",
        "Ξ": "Xi", "Π": "Pi", "Σ": "Sigma", "Φ": "Phi",
        "Ψ": "Psi", "Ω": "Omega",
        # Calculus / set symbols
        "∑": "sum", "∏": "product", "∫": "integral", "∞": "infinity",
        "√": "sqrt",
    }

    # ── Format detection regex ─────────────────────────────────────────
    # Matches LaTeX backslash commands like \frac, \sqrt, \alpha, etc.
    _LATEX_CMD_RE = re.compile(r"\\[a-zA-Z]+")

    def _detect_format(self, input_str: str) -> str:
        """!
        @brief Auto-detect whether input is MathML, LaTeX, or plaintext.

        @details
        Detection heuristics (applied in order):
          1. Starts with '<math' or '<?xml' → 'mathml'
          2. Contains a LaTeX backslash command (e.g. \\frac) → 'latex'
          3. Everything else → 'plaintext'

        @param  input_str  Stripped input string
        @return One of 'mathml', 'latex', or 'plaintext'
        """
        if input_str.startswith("<math") or input_str.startswith("<?xml"):
            return "mathml"
        if self._LATEX_CMD_RE.search(input_str):
            return "latex"
        return "plaintext"

    def parse(self, input_str: str) -> SemanticNode:
        """!
        @brief Parse mathematical input, auto-detecting format.

        @details
        Accepts LaTeX, MathML, or plaintext/Unicode math input.
        The format is detected automatically:
          - MathML if input starts with '<math' or '<?xml'
          - LaTeX  if input contains backslash commands
          - Plaintext otherwise (ASCII math, Unicode symbols, copy-paste)

        @param  input_str  Mathematical expression in any supported format
        @return Root SemanticNode of the parsed expression
        @throws ParseError If parsing fails
        """
        input_str = input_str.strip()
        if not input_str:
            raise ParseError("Empty input string")

        fmt = self._detect_format(input_str)

        if fmt == "mathml":
            return self.parse_mathml(input_str)
        elif fmt == "latex":
            return self.parse_latex(input_str)
        else:
            return self.parse_plaintext(input_str)
    
    def parse_latex(self, latex: str) -> SemanticNode:
        """!
        @brief Parse a LaTeX mathematical expression.
        
        @param latex LaTeX string (with or without $ delimiters)
        @return Root SemanticNode
        @throws ParseError If parsing fails
        """
        # Remove $ delimiters if present
        latex = latex.strip().strip("$").strip()
        
        root = SemanticNode(NodeType.ROOT, metadata={"source": latex})
        self._parse_latex_tokens(latex, root)
        return root
    
    def _parse_latex_tokens(self, latex: str, parent: SemanticNode) -> None:
        """!
        @brief Parse LaTeX tokens and add to parent node.
        
        @param latex LaTeX substring to parse
        @param parent Parent node to add children to
        """
        pos = 0
        while pos < len(latex):
            char = latex[pos]
            
            # Skip whitespace
            if char.isspace():
                pos += 1
                continue
            
            # Handle commands (backslash)
            if char == "\\":
                pos = self._parse_latex_command(latex, pos, parent)
            
            # Handle superscript
            elif char == "^":
                pos = self._parse_latex_super(latex, pos, parent)
            
            # Handle subscript
            elif char == "_":
                pos = self._parse_latex_sub(latex, pos, parent)
            
            # Handle groups
            elif char == "{":
                end = self._find_matching_brace(latex, pos)
                group_content = latex[pos + 1:end]
                group = SemanticNode(NodeType.GROUP)
                self._parse_latex_tokens(group_content, group)
                parent.add_child(group)
                pos = end + 1
            
            elif char == "(":
                parent.add_child(SemanticNode(NodeType.OPERATOR, content="("))
                pos += 1
            
            elif char == ")":
                parent.add_child(SemanticNode(NodeType.OPERATOR, content=")"))
                pos += 1
            
            # Handle operators
            elif char in "+-*/":
                op = self.OPERATORS.get(char, char)
                parent.add_child(SemanticNode(NodeType.OPERATOR, content=op))
                pos += 1
            
            # Handle relations
            elif char in "=<>":
                rel = self.RELATIONS.get(char, char)
                parent.add_child(SemanticNode(NodeType.RELATION, content=rel))
                pos += 1
            
            # Handle numbers
            elif char.isdigit() or (char == "." and pos + 1 < len(latex) and latex[pos + 1].isdigit()):
                num, end = self._parse_number(latex, pos)
                parent.add_child(SemanticNode(NodeType.NUMBER, content=num))
                pos = end
            
            # Handle identifiers (variables)
            elif char.isalpha():
                parent.add_child(SemanticNode(NodeType.IDENTIFIER, content=char))
                pos += 1
            
            else:
                # Unknown character - add as text
                parent.add_child(SemanticNode(NodeType.TEXT, content=char))
                pos += 1
    
    def _parse_latex_command(self, latex: str, pos: int, parent: SemanticNode) -> int:
        """!
        @brief Parse a LaTeX command starting at pos.
        
        @param latex Full LaTeX string
        @param pos Position of the backslash
        @param parent Parent node
        @return Position after the command
        """
        # Extract command name
        match = re.match(r"\\([a-zA-Z]+)", latex[pos:])
        if not match:
            # Single character command like \\
            return pos + 1
        
        cmd = match.group(1)
        cmd_end = pos + len(match.group(0))
        
        # Handle fraction
        if cmd == "frac":
            return self._parse_frac(latex, cmd_end, parent)
        
        # Handle square root
        elif cmd == "sqrt":
            return self._parse_sqrt(latex, cmd_end, parent)
        
        # Handle sum/product/integral
        elif cmd == "sum":
            parent.add_child(SemanticNode(NodeType.SUM, content="∑"))
            return cmd_end
        
        elif cmd == "prod":
            parent.add_child(SemanticNode(NodeType.PRODUCT, content="∏"))
            return cmd_end
        
        elif cmd == "int":
            parent.add_child(SemanticNode(NodeType.INTEGRAL, content="∫"))
            return cmd_end
        
        # Handle Greek letters
        elif cmd.lower() in [k.lower() for k in self.GREEK_LETTERS]:
            # Find the correct case
            for key, value in self.GREEK_LETTERS.items():
                if key.lower() == cmd.lower():
                    parent.add_child(SemanticNode(NodeType.IDENTIFIER, content=value))
                    break
            return cmd_end
        
        # Handle operators
        elif f"\\{cmd}" in self.OPERATORS:
            op = self.OPERATORS[f"\\{cmd}"]
            parent.add_child(SemanticNode(NodeType.OPERATOR, content=op))
            return cmd_end
        
        # Handle relations
        elif f"\\{cmd}" in self.RELATIONS:
            rel = self.RELATIONS[f"\\{cmd}"]
            parent.add_child(SemanticNode(NodeType.RELATION, content=rel))
            return cmd_end
        
        # Handle special symbols
        elif cmd == "infty":
            parent.add_child(SemanticNode(NodeType.IDENTIFIER, content="∞"))
            return cmd_end
        
        # Handle functions (sin, cos, log, etc.)
        elif cmd in ("sin", "cos", "tan", "log", "ln", "exp", "lim"):
            parent.add_child(SemanticNode(NodeType.FUNCTION, content=cmd))
            return cmd_end
        
        # Unknown command - preserve as text
        else:
            parent.add_child(SemanticNode(
                NodeType.TEXT, 
                content=f"\\{cmd}",
                metadata={"unknown_command": True}
            ))
            return cmd_end
    
    def _parse_frac(self, latex: str, pos: int, parent: SemanticNode) -> int:
        """!
        @brief Parse a \\frac{num}{denom} command.
        
        @param latex Full LaTeX string
        @param pos Position after "frac"
        @param parent Parent node
        @return Position after the fraction
        """
        # Parse numerator
        pos = self._skip_whitespace(latex, pos)
        if pos >= len(latex) or latex[pos] != "{":
            raise ParseError("Expected { after \\frac", pos, latex)
        
        num_end = self._find_matching_brace(latex, pos)
        num_content = latex[pos + 1:num_end]
        
        # Parse denominator
        pos = self._skip_whitespace(latex, num_end + 1)
        if pos >= len(latex) or latex[pos] != "{":
            raise ParseError("Expected { for denominator", pos, latex)
        
        denom_end = self._find_matching_brace(latex, pos)
        denom_content = latex[pos + 1:denom_end]
        
        # Create fraction node
        frac = SemanticNode(NodeType.FRACTION)
        
        num_node = SemanticNode(NodeType.GROUP, metadata={"role": "numerator"})
        self._parse_latex_tokens(num_content, num_node)
        frac.add_child(num_node)
        
        denom_node = SemanticNode(NodeType.GROUP, metadata={"role": "denominator"})
        self._parse_latex_tokens(denom_content, denom_node)
        frac.add_child(denom_node)
        
        parent.add_child(frac)
        return denom_end + 1
    
    def _parse_sqrt(self, latex: str, pos: int, parent: SemanticNode) -> int:
        """!
        @brief Parse a \\sqrt{...} or \\sqrt[n]{...} command.
        
        @param latex Full LaTeX string
        @param pos Position after "sqrt"
        @param parent Parent node
        @return Position after the sqrt
        """
        pos = self._skip_whitespace(latex, pos)
        
        # Check for optional n-th root argument
        index_content = None
        if pos < len(latex) and latex[pos] == "[":
            bracket_end = latex.find("]", pos)
            if bracket_end == -1:
                raise ParseError("Unclosed [ in sqrt", pos, latex)
            index_content = latex[pos + 1:bracket_end]
            pos = bracket_end + 1
            pos = self._skip_whitespace(latex, pos)
        
        # Parse radicand
        if pos >= len(latex) or latex[pos] != "{":
            raise ParseError("Expected { after \\sqrt", pos, latex)
        
        brace_end = self._find_matching_brace(latex, pos)
        radicand_content = latex[pos + 1:brace_end]
        
        # Create sqrt node
        if index_content:
            sqrt = SemanticNode(NodeType.NROOT)
            index_node = SemanticNode(NodeType.GROUP, metadata={"role": "index"})
            self._parse_latex_tokens(index_content, index_node)
            sqrt.add_child(index_node)
        else:
            sqrt = SemanticNode(NodeType.SQRT)
        
        radicand = SemanticNode(NodeType.GROUP, metadata={"role": "radicand"})
        self._parse_latex_tokens(radicand_content, radicand)
        sqrt.add_child(radicand)
        
        parent.add_child(sqrt)
        return brace_end + 1
    
    def _parse_latex_super(self, latex: str, pos: int, parent: SemanticNode) -> int:
        """!
        @brief Parse superscript (^).
        
        @param latex Full LaTeX string
        @param pos Position of ^
        @param parent Parent node
        @return Position after superscript
        """
        pos += 1  # Skip ^
        
        # Get the base (previous child)
        if not parent.children:
            raise ParseError("Superscript without base", pos, latex)
        
        base = parent.children.pop()
        
        # Parse the exponent
        if pos < len(latex) and latex[pos] == "{":
            brace_end = self._find_matching_brace(latex, pos)
            exp_content = latex[pos + 1:brace_end]
            pos = brace_end + 1
        else:
            # Single character exponent
            exp_content = latex[pos] if pos < len(latex) else ""
            pos += 1
        
        # Create superscript node
        sup = SemanticNode(NodeType.SUPERSCRIPT)
        sup.add_child(base)
        
        exp = SemanticNode(NodeType.GROUP, metadata={"role": "exponent"})
        self._parse_latex_tokens(exp_content, exp)
        sup.add_child(exp)
        
        parent.add_child(sup)
        return pos
    
    def _parse_latex_sub(self, latex: str, pos: int, parent: SemanticNode) -> int:
        """!
        @brief Parse subscript (_).
        
        @param latex Full LaTeX string  
        @param pos Position of _
        @param parent Parent node
        @return Position after subscript
        """
        pos += 1  # Skip _
        
        # Get the base (previous child)
        if not parent.children:
            raise ParseError("Subscript without base", pos, latex)
        
        base = parent.children.pop()
        
        # Parse the subscript
        if pos < len(latex) and latex[pos] == "{":
            brace_end = self._find_matching_brace(latex, pos)
            sub_content = latex[pos + 1:brace_end]
            pos = brace_end + 1
        else:
            # Single character subscript
            sub_content = latex[pos] if pos < len(latex) else ""
            pos += 1
        
        # Create subscript node
        sub_node = SemanticNode(NodeType.SUBSCRIPT)
        sub_node.add_child(base)
        
        sub_val = SemanticNode(NodeType.GROUP, metadata={"role": "subscript"})
        self._parse_latex_tokens(sub_content, sub_val)
        sub_node.add_child(sub_val)
        
        parent.add_child(sub_node)
        return pos
    
    def _find_matching_brace(self, latex: str, pos: int) -> int:
        """!
        @brief Find the matching closing brace for an opening brace.
        
        @param latex Full LaTeX string
        @param pos Position of opening brace
        @return Position of matching closing brace
        @throws ParseError If no matching brace found
        """
        depth = 1
        pos += 1
        while pos < len(latex) and depth > 0:
            if latex[pos] == "{":
                depth += 1
            elif latex[pos] == "}":
                depth -= 1
            pos += 1
        
        if depth != 0:
            raise ParseError("Unclosed brace", pos, latex)
        
        return pos - 1
    
    def _skip_whitespace(self, latex: str, pos: int) -> int:
        """Skip whitespace characters."""
        while pos < len(latex) and latex[pos].isspace():
            pos += 1
        return pos
    
    def _parse_number(self, latex: str, pos: int) -> tuple[str, int]:
        """!
        @brief Parse a number (integer or decimal).
        
        @param latex Full LaTeX string
        @param pos Starting position
        @return Tuple of (number string, end position)
        """
        start = pos
        has_decimal = False
        
        while pos < len(latex):
            char = latex[pos]
            if char.isdigit():
                pos += 1
            elif char == "." and not has_decimal:
                has_decimal = True
                pos += 1
            else:
                break
        
        return latex[start:pos], pos
    
    def parse_mathml(self, mathml: str) -> SemanticNode:
        """!
        @brief Parse a MathML expression.
        
        @param mathml MathML string
        @return Root SemanticNode
        @throws ParseError If parsing fails
        """
        try:
            # Handle namespace
            mathml = re.sub(r'\sxmlns="[^"]*"', '', mathml)
            tree = ET.fromstring(mathml)
        except ET.ParseError as e:
            raise ParseError(f"Invalid MathML: {e}")
        
        root = SemanticNode(NodeType.ROOT, metadata={"source": mathml})
        self._parse_mathml_element(tree, root)
        return root
    
    def _parse_mathml_element(self, elem: ET.Element, parent: SemanticNode) -> None:
        """!
        @brief Parse a MathML element and add to parent.
        
        @param elem XML element
        @param parent Parent semantic node
        """
        # Get tag without namespace
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        
        if tag == "math":
            for child in elem:
                self._parse_mathml_element(child, parent)
        
        elif tag == "mrow":
            group = SemanticNode(NodeType.GROUP)
            for child in elem:
                self._parse_mathml_element(child, group)
            parent.add_child(group)
        
        elif tag == "mfrac":
            frac = SemanticNode(NodeType.FRACTION)
            children = list(elem)
            if len(children) >= 2:
                num = SemanticNode(NodeType.GROUP, metadata={"role": "numerator"})
                self._parse_mathml_element(children[0], num)
                frac.add_child(num)
                
                denom = SemanticNode(NodeType.GROUP, metadata={"role": "denominator"})
                self._parse_mathml_element(children[1], denom)
                frac.add_child(denom)
            parent.add_child(frac)
        
        elif tag == "msup":
            sup = SemanticNode(NodeType.SUPERSCRIPT)
            children = list(elem)
            if len(children) >= 2:
                base = SemanticNode(NodeType.GROUP, metadata={"role": "base"})
                self._parse_mathml_element(children[0], base)
                sup.add_child(base)
                
                exp = SemanticNode(NodeType.GROUP, metadata={"role": "exponent"})
                self._parse_mathml_element(children[1], exp)
                sup.add_child(exp)
            parent.add_child(sup)
        
        elif tag == "msub":
            sub = SemanticNode(NodeType.SUBSCRIPT)
            children = list(elem)
            if len(children) >= 2:
                base = SemanticNode(NodeType.GROUP, metadata={"role": "base"})
                self._parse_mathml_element(children[0], base)
                sub.add_child(base)
                
                subscript = SemanticNode(NodeType.GROUP, metadata={"role": "subscript"})
                self._parse_mathml_element(children[1], subscript)
                sub.add_child(subscript)
            parent.add_child(sub)
        
        elif tag == "msqrt":
            sqrt = SemanticNode(NodeType.SQRT)
            radicand = SemanticNode(NodeType.GROUP, metadata={"role": "radicand"})
            for child in elem:
                self._parse_mathml_element(child, radicand)
            sqrt.add_child(radicand)
            parent.add_child(sqrt)
        
        elif tag == "mi":
            # Identifier
            text = (elem.text or "").strip()
            parent.add_child(SemanticNode(NodeType.IDENTIFIER, content=text))
        
        elif tag == "mn":
            # Number
            text = (elem.text or "").strip()
            parent.add_child(SemanticNode(NodeType.NUMBER, content=text))
        
        elif tag == "mo":
            # Operator
            text = (elem.text or "").strip()
            if text in "=<>≤≥≠":
                parent.add_child(SemanticNode(NodeType.RELATION, content=text))
            else:
                parent.add_child(SemanticNode(NodeType.OPERATOR, content=text))
        
        elif tag == "mtext":
            text = (elem.text or "").strip()
            parent.add_child(SemanticNode(NodeType.TEXT, content=text))
        
        else:
            # Unknown element - try to parse children
            for child in elem:
                self._parse_mathml_element(child, parent)

    # =====================================================================
    # PLAINTEXT / UNICODE MATH PARSER
    # =====================================================================

    def parse_plaintext(self, text: str) -> SemanticNode:
        """!
        @brief Parse a plaintext or Unicode math expression.

        @details
        Handles everyday copy-paste math formats including:
          - Fractions:      a/b, (a+b)/(c-d)
          - Exponents:      x^2, x^{10}, x**2
          - Subscripts:     x_i, x_{10}
          - Square root:    sqrt(x), √(x), √x
          - Unicode digits: x², x₁, y³
          - Unicode Greek:  π, α, β, Σ, Δ
          - Unicode ops:    ×, ÷, ±, ≤, ≥, ≠
          - Functions:      sin(x), cos(x), log(x), ln(x), exp(x)
          - Relations:      =, <, >, <=, >=, !=

        The parser first normalises the input (expanding ** to ^,
        converting Unicode super/subscript runs, and mapping Unicode
        symbols) and then tokenises the result into a SemanticNode tree.

        @param  text  Plaintext math string
        @return Root SemanticNode of the parsed expression
        @throws ParseError If parsing fails
        """
        text = text.strip()
        if not text:
            raise ParseError("Empty plaintext input")

        # Step 1 – normalise the raw string
        normalised = self._normalise_plaintext(text)

        root = SemanticNode(NodeType.ROOT,
                            metadata={"source": text, "format": "plaintext"})
        self._parse_plaintext_tokens(normalised, root)
        return root

    # ── Normalisation ────────────────────────────────────────────────────

    def _normalise_plaintext(self, text: str) -> str:
        """!
        @brief Normalise plaintext math to a canonical token-friendly form.

        @details
        Performs the following transformations (in order):
          1. Convert Unicode super/subscript digit runs into ^{...} / _{...}
          2. Replace ** with ^
          3. Map Unicode symbols (×, ÷, Greek, √, ∞, etc.) to ASCII tokens
          4. Normalise whitespace

        @param  text  Raw plaintext input
        @return Normalised string ready for tokenisation
        """
        result: list[str] = []
        i = 0
        while i < len(text):
            ch = text[i]

            # ── Unicode superscript run → ^{digits} ─────────────────
            if ch in self.UNICODE_SUPERSCRIPT_MAP:
                sup_chars: list[str] = []
                while i < len(text) and text[i] in self.UNICODE_SUPERSCRIPT_MAP:
                    sup_chars.append(self.UNICODE_SUPERSCRIPT_MAP[text[i]])
                    i += 1
                result.append("^{" + "".join(sup_chars) + "}")
                continue

            # ── Unicode subscript run → _{digits} ───────────────────
            if ch in self.UNICODE_SUBSCRIPT_MAP:
                sub_chars: list[str] = []
                while i < len(text) and text[i] in self.UNICODE_SUBSCRIPT_MAP:
                    sub_chars.append(self.UNICODE_SUBSCRIPT_MAP[text[i]])
                    i += 1
                result.append("_{" + "".join(sub_chars) + "}")
                continue

            # ── ** → ^ ──────────────────────────────────────────────
            if ch == "*" and i + 1 < len(text) and text[i + 1] == "*":
                result.append("^")
                i += 2
                continue

            # ── Unicode symbol mapping ──────────────────────────────
            if ch in self.UNICODE_SYMBOL_MAP:
                mapped = self.UNICODE_SYMBOL_MAP[ch]
                # Greek letters / function names are multi-char tokens
                if mapped == "sqrt":
                    result.append("sqrt")
                elif mapped == "sum":
                    result.append("∑")
                elif mapped == "product":
                    result.append("∏")
                elif mapped == "integral":
                    result.append("∫")
                elif mapped == "infinity":
                    result.append("∞")
                elif len(mapped) > 1 and mapped.isalpha():
                    # Greek letter name – wrap so tokeniser sees it
                    result.append(f"«{mapped}»")
                else:
                    result.append(mapped)
                i += 1
                continue

            # ── Pass through everything else ────────────────────────
            result.append(ch)
            i += 1

        return "".join(result)

    # ── Tokeniser / recursive-descent parser ─────────────────────────

    # Regex for named math functions handled as FUNCTION nodes.
    _FUNC_RE = re.compile(
        r"^(sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|"
        r"log|ln|exp|lim|sec|csc|cot)\b"
    )

    def _parse_plaintext_tokens(
        self, text: str, parent: SemanticNode
    ) -> None:
        """!
        @brief Tokenise normalised plaintext and add nodes to parent.

        @details
        Walks the string character-by-character, recognising:
          - Numbers (integer and decimal)
          - Identifiers (single Latin letters) and Greek «name» tokens
          - Operators: + - * /
          - Relations: =  < > <= >= != ≈ ≡
          - Parentheses ( )
          - Superscript ^ and subscript _
          - sqrt(...) function calls
          - Named math functions: sin, cos, etc.
          - Special symbols: ∑ ∏ ∫ ∞ ± ∓

        @param  text    Normalised plaintext string
        @param  parent  Parent SemanticNode to append children to
        """
        pos = 0
        length = len(text)

        while pos < length:
            ch = text[pos]

            # ── Skip whitespace ─────────────────────────────────────
            if ch.isspace():
                pos += 1
                continue

            # ── Greek letter tokens wrapped by normaliser ───────────
            if ch == "«":
                end = text.find("»", pos)
                if end == -1:
                    end = length
                name = text[pos + 1:end]
                # Resolve to Unicode glyph via GREEK_LETTERS map
                glyph = self.GREEK_LETTERS.get(
                    name, self.GREEK_LETTERS.get(name.lower(), name)
                )
                parent.add_child(
                    SemanticNode(NodeType.IDENTIFIER, content=glyph)
                )
                pos = end + 1
                continue

            # ── Special single-char symbols ─────────────────────────
            if ch == "∑":
                parent.add_child(SemanticNode(NodeType.SUM, content="∑"))
                pos += 1
                continue
            if ch == "∏":
                parent.add_child(SemanticNode(NodeType.PRODUCT, content="∏"))
                pos += 1
                continue
            if ch == "∫":
                parent.add_child(
                    SemanticNode(NodeType.INTEGRAL, content="∫")
                )
                pos += 1
                continue
            if ch == "∞":
                parent.add_child(
                    SemanticNode(NodeType.IDENTIFIER, content="∞")
                )
                pos += 1
                continue
            if ch == "±":
                parent.add_child(SemanticNode(NodeType.OPERATOR, content="±"))
                pos += 1
                continue
            if ch == "∓":
                parent.add_child(SemanticNode(NodeType.OPERATOR, content="∓"))
                pos += 1
                continue

            # ── sqrt(...) or sqrt followed by single token ──────────
            if text[pos:pos + 4] == "sqrt":
                pos = self._parse_plaintext_sqrt(text, pos + 4, parent)
                continue

            # ── Named math functions (sin, cos, log, …) ────────────
            func_m = self._FUNC_RE.match(text[pos:])
            if func_m:
                fname = func_m.group(1)
                parent.add_child(
                    SemanticNode(NodeType.FUNCTION, content=fname)
                )
                pos += len(fname)
                continue

            # ── Superscript ^ ───────────────────────────────────────
            if ch == "^":
                pos = self._parse_plaintext_super(text, pos, parent)
                continue

            # ── Subscript _ ─────────────────────────────────────────
            if ch == "_":
                pos = self._parse_plaintext_sub(text, pos, parent)
                continue

            # ── Parenthesised group ─────────────────────────────────
            if ch == "(":
                # Find matching close paren
                paren_end = self._find_matching_paren(text, pos)
                inner = text[pos + 1:paren_end]
                group = SemanticNode(NodeType.GROUP)
                self._parse_plaintext_tokens(inner, group)
                parent.add_child(group)
                pos = paren_end + 1
                continue

            if ch == ")":
                # Stray close paren – add as operator for robustness
                parent.add_child(
                    SemanticNode(NodeType.OPERATOR, content=")")
                )
                pos += 1
                continue

            # ── Multi-char relational operators (<= >= != ≈ ≡) ─────
            two = text[pos:pos + 2]
            if two in ("<=", ">=", "!="):
                rel_map = {"<=": "≤", ">=": "≥", "!=": "≠"}
                parent.add_child(
                    SemanticNode(NodeType.RELATION, content=rel_map[two])
                )
                pos += 2
                continue
            if ch in ("≈", "≡"):
                parent.add_child(
                    SemanticNode(NodeType.RELATION, content=ch)
                )
                pos += 1
                continue

            # ── Single-char operators ───────────────────────────────
            if ch in "+-":
                parent.add_child(
                    SemanticNode(NodeType.OPERATOR, content=ch)
                )
                pos += 1
                continue
            if ch == "*":
                parent.add_child(
                    SemanticNode(NodeType.OPERATOR, content="×")
                )
                pos += 1
                continue

            # ── Division / potential fraction ───────────────────────
            if ch == "/":
                parent.add_child(
                    SemanticNode(NodeType.OPERATOR, content="÷")
                )
                pos += 1
                continue

            # ── Single-char relations ───────────────────────────────
            if ch in "=<>":
                parent.add_child(
                    SemanticNode(NodeType.RELATION, content=ch)
                )
                pos += 1
                continue

            # ── Numbers ─────────────────────────────────────────────
            if ch.isdigit() or (
                ch == "." and pos + 1 < length and text[pos + 1].isdigit()
            ):
                num, end = self._parse_number(text, pos)
                parent.add_child(
                    SemanticNode(NodeType.NUMBER, content=num)
                )
                pos = end
                continue

            # ── Identifiers (single letters) ────────────────────────
            if ch.isalpha():
                parent.add_child(
                    SemanticNode(NodeType.IDENTIFIER, content=ch)
                )
                pos += 1
                continue

            # ── Braces (used after normalisation for ^{} / _{}) ────
            if ch == "{":
                brace_end = self._find_matching_brace(text, pos)
                inner = text[pos + 1:brace_end]
                group = SemanticNode(NodeType.GROUP)
                self._parse_plaintext_tokens(inner, group)
                parent.add_child(group)
                pos = brace_end + 1
                continue

            # ── Fallback – unknown character as TEXT ─────────────────
            parent.add_child(SemanticNode(NodeType.TEXT, content=ch))
            pos += 1

    # ── Plaintext helper: sqrt ───────────────────────────────────────

    def _parse_plaintext_sqrt(
        self, text: str, pos: int, parent: SemanticNode
    ) -> int:
        """!
        @brief Parse sqrt(...) or sqrt followed by a single token.

        @param  text    Full normalised string
        @param  pos     Position immediately after "sqrt"
        @param  parent  Parent node
        @return Position after the sqrt expression
        """
        pos = self._skip_whitespace(text, pos)

        sqrt_node = SemanticNode(NodeType.SQRT)
        radicand = SemanticNode(NodeType.GROUP, metadata={"role": "radicand"})

        if pos < len(text) and text[pos] == "(":
            paren_end = self._find_matching_paren(text, pos)
            inner = text[pos + 1:paren_end]
            self._parse_plaintext_tokens(inner, radicand)
            pos = paren_end + 1
        elif pos < len(text) and text[pos] == "{":
            brace_end = self._find_matching_brace(text, pos)
            inner = text[pos + 1:brace_end]
            self._parse_plaintext_tokens(inner, radicand)
            pos = brace_end + 1
        elif pos < len(text):
            # Single character / number after sqrt
            if text[pos].isdigit():
                num, end = self._parse_number(text, pos)
                radicand.add_child(
                    SemanticNode(NodeType.NUMBER, content=num)
                )
                pos = end
            elif text[pos].isalpha():
                radicand.add_child(
                    SemanticNode(NodeType.IDENTIFIER, content=text[pos])
                )
                pos += 1
            else:
                radicand.add_child(
                    SemanticNode(NodeType.TEXT, content=text[pos])
                )
                pos += 1

        sqrt_node.add_child(radicand)
        parent.add_child(sqrt_node)
        return pos

    # ── Plaintext helper: superscript ────────────────────────────────

    def _parse_plaintext_super(
        self, text: str, pos: int, parent: SemanticNode
    ) -> int:
        """!
        @brief Parse superscript (^) in plaintext.

        @param  text    Full normalised string
        @param  pos     Position of '^'
        @param  parent  Parent node
        @return Position after the superscript
        """
        pos += 1  # skip ^

        if not parent.children:
            raise ParseError("Superscript without base", pos, text)
        base = parent.children.pop()

        # Parse exponent
        if pos < len(text) and text[pos] == "{":
            brace_end = self._find_matching_brace(text, pos)
            exp_content = text[pos + 1:brace_end]
            pos = brace_end + 1
        elif pos < len(text) and text[pos] == "(":
            paren_end = self._find_matching_paren(text, pos)
            exp_content = text[pos + 1:paren_end]
            pos = paren_end + 1
        elif pos < len(text):
            # Single character exponent
            exp_content = text[pos]
            pos += 1
        else:
            exp_content = ""

        sup = SemanticNode(NodeType.SUPERSCRIPT)
        sup.add_child(base)
        exp_node = SemanticNode(NodeType.GROUP, metadata={"role": "exponent"})
        self._parse_plaintext_tokens(exp_content, exp_node)
        sup.add_child(exp_node)
        parent.add_child(sup)
        return pos

    # ── Plaintext helper: subscript ──────────────────────────────────

    def _parse_plaintext_sub(
        self, text: str, pos: int, parent: SemanticNode
    ) -> int:
        """!
        @brief Parse subscript (_) in plaintext.

        @param  text    Full normalised string
        @param  pos     Position of '_'
        @param  parent  Parent node
        @return Position after the subscript
        """
        pos += 1  # skip _

        if not parent.children:
            raise ParseError("Subscript without base", pos, text)
        base = parent.children.pop()

        # Parse subscript value
        if pos < len(text) and text[pos] == "{":
            brace_end = self._find_matching_brace(text, pos)
            sub_content = text[pos + 1:brace_end]
            pos = brace_end + 1
        elif pos < len(text) and text[pos] == "(":
            paren_end = self._find_matching_paren(text, pos)
            sub_content = text[pos + 1:paren_end]
            pos = paren_end + 1
        elif pos < len(text):
            sub_content = text[pos]
            pos += 1
        else:
            sub_content = ""

        sub_node = SemanticNode(NodeType.SUBSCRIPT)
        sub_node.add_child(base)
        sub_val = SemanticNode(NodeType.GROUP, metadata={"role": "subscript"})
        self._parse_plaintext_tokens(sub_content, sub_val)
        sub_node.add_child(sub_val)
        parent.add_child(sub_node)
        return pos

    # ── Plaintext helper: matching parenthesis ───────────────────────

    def _find_matching_paren(self, text: str, pos: int) -> int:
        """!
        @brief Find the closing ')' that matches the '(' at pos.

        @param  text  Full string
        @param  pos   Position of opening '('
        @return Position of matching ')'
        @throws ParseError If no match found
        """
        depth = 1
        pos += 1
        while pos < len(text) and depth > 0:
            if text[pos] == "(":
                depth += 1
            elif text[pos] == ")":
                depth -= 1
            pos += 1
        if depth != 0:
            raise ParseError("Unclosed parenthesis", pos, text)
        return pos - 1
