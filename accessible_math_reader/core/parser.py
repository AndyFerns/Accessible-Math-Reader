"""!
@file core/parser.py
@brief Math expression parser for LaTeX and MathML input.

@details
Converts LaTeX and MathML strings into a semantic AST representation.
Supports common mathematical constructs including fractions, exponents,
subscripts, Greek letters, and operators.

@author Accessible Math Reader Contributors
@version 0.1.0
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
    @brief Parser for converting LaTeX/MathML to semantic representation.
    
    @details
    Provides a unified interface for parsing mathematical notation
    into a format-agnostic semantic tree.
    
    @section parser_example Example Usage
    @code{.py}
    parser = MathParser()
    
    # Parse LaTeX
    tree = parser.parse(r"\\frac{a}{b}")
    
    # Parse MathML
    tree = parser.parse("<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>")
    
    # Force specific format
    tree = parser.parse_latex(r"\\frac{a}{b}")
    tree = parser.parse_mathml("<math>...</math>")
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
    
    def parse(self, input_str: str) -> SemanticNode:
        """!
        @brief Parse mathematical input, auto-detecting format.
        
        @param input_str LaTeX or MathML string
        @return Root SemanticNode of the parsed expression
        @throws ParseError If parsing fails
        """
        input_str = input_str.strip()
        
        if input_str.startswith("<math") or input_str.startswith("<?xml"):
            return self.parse_mathml(input_str)
        else:
            return self.parse_latex(input_str)
    
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
