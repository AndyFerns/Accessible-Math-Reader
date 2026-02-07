"""!
@file braille/ueb.py
@brief Unified English Braille (UEB) converter for mathematical notation.

@details
Implements UEB Technical guidelines for mathematics. UEB is the international
standard for English Braille and includes provisions for mathematical content.

@see https://www.brailleauthority.org/ueb/ueb.html

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from accessible_math_reader.core.semantic import SemanticNode, NodeType
from accessible_math_reader.core.renderer import BaseRenderer

if TYPE_CHECKING:
    from accessible_math_reader.config import Config


class UEBConverter(BaseRenderer):
    """!
    @brief Converts semantic math trees to UEB Braille.
    
    @details
    Implements Unified English Braille technical notation for mathematics.
    UEB uses different conventions than Nemeth for some constructs.
    
    @section ueb_example Example Usage
    @code{.py}
    from accessible_math_reader import MathParser
    from accessible_math_reader.braille.ueb import UEBConverter
    
    parser = MathParser()
    converter = UEBConverter()
    
    tree = parser.parse(r"\\frac{1}{2}")
    braille = converter.render(tree)
    @endcode
    """
    
    # UEB digits (preceded by numeric indicator when needed)
    DIGITS = {
        "0": "⠚", "1": "⠁", "2": "⠃", "3": "⠉", "4": "⠙",
        "5": "⠑", "6": "⠋", "7": "⠛", "8": "⠓", "9": "⠊",
    }
    
    # UEB letters (same as literary Braille)
    LETTERS = {
        "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙", "e": "⠑",
        "f": "⠋", "g": "⠛", "h": "⠓", "i": "⠊", "j": "⠚",
        "k": "⠅", "l": "⠇", "m": "⠍", "n": "⠝", "o": "⠕",
        "p": "⠏", "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞",
        "u": "⠥", "v": "⠧", "w": "⠺", "x": "⠭", "y": "⠽",
        "z": "⠵",
    }
    
    # UEB operators
    OPERATORS = {
        "+": "⠬",    # Plus
        "-": "⠤",    # Minus/hyphen
        "−": "⠤",    # Minus sign
        "×": "⠐⠦",  # Times
        "·": "⠐⠲",  # Dot multiply
        "÷": "⠐⠌",  # Division
        "(": "⠐⠣",  # Left paren
        ")": "⠐⠜",  # Right paren
        "[": "⠨⠣",  # Left bracket
        "]": "⠨⠜",  # Right bracket
    }
    
    # UEB relations
    RELATIONS = {
        "=": "⠐⠶",   # Equals
        "<": "⠐⠪",   # Less than
        ">": "⠐⠕",   # Greater than
        "≤": "⠐⠪⠶", # Less than or equal
        "≥": "⠐⠕⠶", # Greater than or equal
        "≠": "⠐⠶⠈⠱", # Not equal
    }
    
    # UEB structural symbols
    NUMERIC_INDICATOR = "⠼"       # Numeric passage/symbol
    GRADE1_INDICATOR = "⠰"        # Grade 1 symbol
    CAPITAL_INDICATOR = "⠠"       # Capital letter
    FRACTION_OPEN = "⠷"           # Opening fraction indicator
    FRACTION_LINE = "⠌"           # Horizontal line
    FRACTION_CLOSE = "⠾"          # Closing fraction indicator
    
    def __init__(self, config: Config | None = None) -> None:
        """!
        @brief Initialize UEB converter.
        
        @param config Configuration object
        """
        super().__init__(config)
    
    def render(self, node: SemanticNode) -> str:
        """!
        @brief Render semantic node to UEB Braille.
        
        @param node Semantic node to render
        @return UEB Braille string
        """
        method = getattr(self, f"_render_{node.node_type.name.lower()}", None)
        if method:
            return method(node)
        return self._render_default(node)
    
    def _render_root(self, node: SemanticNode) -> str:
        """Render root node."""
        return "".join(self.render(c) for c in node.children)
    
    def _render_group(self, node: SemanticNode) -> str:
        """Render group node."""
        return "".join(self.render(c) for c in node.children)
    
    def _render_number(self, node: SemanticNode) -> str:
        """!
        @brief Render number with numeric indicator.
        
        @param node Number node
        @return UEB Braille for number
        """
        content = node.content
        result = self.NUMERIC_INDICATOR
        
        for char in content:
            if char in self.DIGITS:
                result += self.DIGITS[char]
            elif char == ".":
                result += "⠲"  # Decimal point
            else:
                result += char
        
        return result
    
    def _render_identifier(self, node: SemanticNode) -> str:
        """!
        @brief Render identifier.
        
        @param node Identifier node
        @return UEB Braille for identifier
        """
        content = node.content
        result = ""
        
        for char in content:
            if char.isupper() and char.lower() in self.LETTERS:
                result += self.CAPITAL_INDICATOR + self.LETTERS[char.lower()]
            elif char.lower() in self.LETTERS:
                result += self.LETTERS[char.lower()]
            else:
                result += char
        
        return result
    
    def _render_operator(self, node: SemanticNode) -> str:
        """Render operator."""
        return self.OPERATORS.get(node.content, node.content)
    
    def _render_relation(self, node: SemanticNode) -> str:
        """Render relation."""
        return self.RELATIONS.get(node.content, node.content)
    
    def _render_fraction(self, node: SemanticNode) -> str:
        """!
        @brief Render UEB fraction.
        
        @param node Fraction node
        @return UEB fraction representation
        """
        result = self.FRACTION_OPEN
        
        if node.children:
            result += self.render(node.children[0])
        
        result += self.FRACTION_LINE
        
        if len(node.children) > 1:
            result += self.render(node.children[1])
        
        result += self.FRACTION_CLOSE
        return result
    
    def _render_superscript(self, node: SemanticNode) -> str:
        """Render superscript."""
        result = ""
        
        if node.children:
            result += self.render(node.children[0])
        
        result += "⠔"  # UEB superscript indicator
        
        if len(node.children) > 1:
            result += self.render(node.children[1])
        
        return result
    
    def _render_subscript(self, node: SemanticNode) -> str:
        """Render subscript."""
        result = ""
        
        if node.children:
            result += self.render(node.children[0])
        
        result += "⠢"  # UEB subscript indicator
        
        if len(node.children) > 1:
            result += self.render(node.children[1])
        
        return result
    
    def _render_sqrt(self, node: SemanticNode) -> str:
        """Render square root."""
        result = "⠩"  # UEB radical indicator
        
        if node.children:
            result += self.render(node.children[0])
        
        result += "⠱"  # End radical
        return result
    
    def _render_function(self, node: SemanticNode) -> str:
        """Render function name."""
        return "".join(self.LETTERS.get(c, c) for c in node.content.lower())
    
    def _render_text(self, node: SemanticNode) -> str:
        """Render text."""
        result = ""
        for char in node.content:
            if char.isupper() and char.lower() in self.LETTERS:
                result += self.CAPITAL_INDICATOR + self.LETTERS[char.lower()]
            elif char.lower() in self.LETTERS:
                result += self.LETTERS[char.lower()]
            elif char in self.DIGITS:
                result += self.DIGITS[char]
            elif char == " ":
                result += "⠀"
            else:
                result += char
        return result
    
    def _render_default(self, node: SemanticNode) -> str:
        """Default rendering."""
        if node.content:
            return self._render_text(SemanticNode(NodeType.TEXT, content=node.content))
        return "".join(self.render(c) for c in node.children)
