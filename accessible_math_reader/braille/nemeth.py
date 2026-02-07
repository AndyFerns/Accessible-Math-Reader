"""!
@file braille/nemeth.py
@brief Nemeth Braille Code converter for mathematical notation.

@details
Implements the Nemeth Braille Code for Mathematics, the standard
mathematical Braille notation used in the United States. This includes
proper handling of:
- Numeric indicator for digits
- Letter indicator for letters in math context
- Structural indicators for fractions, exponents, etc.

@see https://www.brailleauthority.org/mathscience/nemeth1972.pdf

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from accessible_math_reader.core.semantic import SemanticNode, NodeType
from accessible_math_reader.core.renderer import BaseRenderer

if TYPE_CHECKING:
    from accessible_math_reader.config import Config


class NemethConverter(BaseRenderer):
    """!
    @brief Converts semantic math trees to Nemeth Braille.
    
    @details
    Implements Nemeth Braille Code conversion following standard rules.
    The Nemeth code is specifically designed for mathematical and
    scientific notation in Braille.
    
    @section nemeth_example Example Usage
    @code{.py}
    from accessible_math_reader import MathParser
    from accessible_math_reader.braille.nemeth import NemethConverter
    
    parser = MathParser()
    converter = NemethConverter()
    
    tree = parser.parse(r"\\frac{1}{2}")
    braille = converter.render(tree)
    # Output: "⠹⠂⠌⠆⠼" (Nemeth fraction encoding)
    @endcode
    
    @section nemeth_codes Key Nemeth Codes
    - Numeric indicator: ⠼ (dots 3456)
    - Fraction open: ⠹ (dots 1256)
    - Fraction line: ⠌ (dots 34)
    - Fraction close: ⠼ (dots 3456)
    - Superscript: ⠘ (dots 45)
    - Subscript: ⠰ (dots 56)
    - Square root: ⠜ (dots 345)
    """
    
    # =========================================================================
    # Nemeth Braille Character Mappings
    # =========================================================================
    
    # Digits in Nemeth use the same cells as letters a-j but are preceded
    # by the numeric indicator when starting a number
    DIGITS = {
        "0": "⠴",  # Dots 356
        "1": "⠂",  # Dot 2
        "2": "⠆",  # Dots 23
        "3": "⠒",  # Dots 25
        "4": "⠲",  # Dots 256
        "5": "⠢",  # Dots 26
        "6": "⠖",  # Dots 235
        "7": "⠶",  # Dots 2356
        "8": "⠦",  # Dots 236
        "9": "⠔",  # Dots 35
    }
    
    # Lowercase letters (same as standard Braille)
    LETTERS = {
        "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙", "e": "⠑",
        "f": "⠋", "g": "⠛", "h": "⠓", "i": "⠊", "j": "⠚",
        "k": "⠅", "l": "⠇", "m": "⠍", "n": "⠝", "o": "⠕",
        "p": "⠏", "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞",
        "u": "⠥", "v": "⠧", "w": "⠺", "x": "⠭", "y": "⠽",
        "z": "⠵",
    }
    
    # Greek letters using Nemeth Greek letter indicator (⠨)
    GREEK = {
        "α": "⠨⠁", "β": "⠨⠃", "γ": "⠨⠛", "δ": "⠨⠙",
        "ε": "⠨⠑", "ζ": "⠨⠵", "η": "⠨⠱", "θ": "⠨⠹",
        "ι": "⠨⠊", "κ": "⠨⠅", "λ": "⠨⠇", "μ": "⠨⠍",
        "ν": "⠨⠝", "ξ": "⠨⠭", "π": "⠨⠏", "ρ": "⠨⠗",
        "σ": "⠨⠎", "τ": "⠨⠞", "υ": "⠨⠥", "φ": "⠨⠋",
        "χ": "⠨⠯", "ψ": "⠨⠽", "ω": "⠨⠺",
        # Capital Greek (add capital indicator ⠠)
        "Α": "⠠⠨⠁", "Β": "⠠⠨⠃", "Γ": "⠠⠨⠛", "Δ": "⠠⠨⠙",
        "Θ": "⠠⠨⠹", "Λ": "⠠⠨⠇", "Π": "⠠⠨⠏", "Σ": "⠠⠨⠎",
        "Φ": "⠠⠨⠋", "Ψ": "⠠⠨⠽", "Ω": "⠠⠨⠺",
    }
    
    # Mathematical operators
    OPERATORS = {
        "+": "⠬",    # Plus (dots 346)
        "-": "⠤",    # Minus (dots 36)
        "−": "⠤",    # Minus sign variant
        "×": "⠡",    # Times (dots 16)
        "·": "⠡",    # Dot multiply
        "÷": "⠌",    # Division (dots 34)
        "±": "⠬⠤",  # Plus-minus
        "(": "⠷",    # Left paren (dots 12356)
        ")": "⠾",    # Right paren (dots 23456)
        "[": "⠈⠷",  # Left bracket
        "]": "⠈⠾",  # Right bracket
    }
    
    # Relations
    RELATIONS = {
        "=": "⠀⠿⠀",  # Equals with spaces (dots 123456)
        "<": "⠀⠪⠀",  # Less than (dots 126)
        ">": "⠀⠻⠀",  # Greater than (dots 12456)
        "≤": "⠀⠪⠿⠀",  # Less than or equal
        "≥": "⠀⠻⠿⠀",  # Greater than or equal
        "≠": "⠀⠿⠈⠱⠀",  # Not equal
        "≈": "⠀⠈⠿⠀",  # Approximately equal
    }
    
    # Structural indicators
    NUMERIC_INDICATOR = "⠼"      # Dots 3456 - precedes numbers
    LETTER_INDICATOR = "⠰"       # Dots 56 - precedes single letters
    FRACTION_OPEN = "⠹"          # Dots 1256
    FRACTION_LINE = "⠌"          # Dots 34
    FRACTION_CLOSE = "⠼"         # Dots 3456
    SUPERSCRIPT_IND = "⠘"        # Dots 45
    SUBSCRIPT_IND = "⠰"          # Dots 56
    BASELINE_IND = "⠐"           # Dot 5 - return to baseline after scripts
    SQRT_OPEN = "⠜"              # Dots 345
    SQRT_CLOSE = "⠻"             # Dots 12456
    
    # === PHASE 3 ADDITIONS: Missing Nemeth Indicators ===
    # Multipurpose indicator (used for various special contexts)
    MULTIPURPOSE_IND = "⠸"       # Dots 456 - multipurpose prefix
    
    # Grade 1 mode indicators (for letter sequences without contractions)
    GRADE1_SYMBOL_IND = "⠰⠰"    # Dots 56, 56 - grade 1 symbol indicator
    GRADE1_WORD_IND = "⠰⠰⠰"     # Dots 56, 56, 56 - grade 1 word indicator
    
    # Shape indicators (for geometric shapes)
    SHAPE_IND = "⠫"              # Dots 1246 - shape indicator prefix
    
    # Comparison and set theory
    SUBSET = "⠸⠐⠅"              # Subset symbol
    SUPERSET = "⠸⠐⠂⠅"          # Superset symbol
    ELEMENT_OF = "⠈⠑"           # Element of set
    NOT_ELEMENT = "⠈⠑⠌"        # Not an element of
    
    def __init__(self, config: Config | None = None) -> None:
        """!
        @brief Initialize Nemeth converter.
        
        @param config Configuration object
        """
        super().__init__(config)
        
        # === MODE STATE MACHINE ===
        # Track current mode for proper indicator insertion
        # Modes: NEUTRAL, NUMERIC, LETTER, MATH
        self._current_mode = 'NEUTRAL'
        
        # Track if we need baseline indicator after scripts
        self._needs_baseline = False
        
        # === PHASE 3: ERROR HANDLING ===
        # Track unsupported constructs for graceful fallback
        self._unsupported_nodes: list[str] = []
    
    def render(self, node: SemanticNode) -> str:
        """!
        @brief Render semantic node to Nemeth Braille.
        
        @param node Semantic node to render
        @return Nemeth Braille string
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
        @brief Render a number with numeric indicator.
        
        @details
        Numbers in Nemeth are prefixed with the numeric indicator (⠼).
        Each digit is then converted to its Nemeth representation.
        
        @param node Number node
        @return Nemeth Braille for the number
        """
        content = node.content
        result = self.NUMERIC_INDICATOR
        
        for char in content:
            if char in self.DIGITS:
                result += self.DIGITS[char]
            elif char == ".":
                result += "⠨"  # Decimal point
            else:
                result += char
        
        return result
    
    def _render_identifier(self, node: SemanticNode) -> str:
        """!
        @brief Render an identifier (variable or Greek letter).
        
        @param node Identifier node
        @return Nemeth Braille for the identifier
        """
        content = node.content
        
        # Check Greek letters first
        if content in self.GREEK:
            return self.GREEK[content]
        
        # Infinity
        if content == "∞":
            return "⠠⠿"  # Nemeth infinity symbol
        
        # Single letter - may need letter indicator in some contexts
        if len(content) == 1 and content.lower() in self.LETTERS:
            letter = self.LETTERS[content.lower()]
            if content.isupper():
                return "⠠" + letter  # Capital indicator
            return letter
        
        # Multi-letter identifier
        result = ""
        for char in content.lower():
            if char in self.LETTERS:
                result += self.LETTERS[char]
            else:
                result += char
        return result
    
    def _render_operator(self, node: SemanticNode) -> str:
        """!
        @brief Render operator symbol.
        
        @param node Operator node
        @return Nemeth Braille for operator
        """
        return self.OPERATORS.get(node.content, node.content)
    
    def _render_relation(self, node: SemanticNode) -> str:
        """!
        @brief Render relation symbol.
        
        @param node Relation node
        @return Nemeth Braille for relation
        """
        return self.RELATIONS.get(node.content, node.content)
    
    def _render_fraction(self, node: SemanticNode) -> str:
        """!
        @brief Render fraction in Nemeth format.
        
        @details
        Nemeth fractions use:
        - ⠹ (fraction open)
        - numerator
        - ⠌ (fraction line)
        - denominator  
        - ⠼ (fraction close)
        
        @param node Fraction node with numerator and denominator children
        @return Nemeth fraction
        """
        result = self.FRACTION_OPEN
        
        # Numerator
        if node.children:
            result += self.render(node.children[0])
        
        result += self.FRACTION_LINE
        
        # Denominator
        if len(node.children) > 1:
            result += self.render(node.children[1])
        
        result += self.FRACTION_CLOSE
        return result
    
    def _render_superscript(self, node: SemanticNode) -> str:
        """!
        @brief Render superscript/exponent.
        
        @details
        Uses superscript indicator ⠘ before the exponent.
        Returns to baseline with ⠐ if followed by more content.
        
        @param node Superscript node
        @return Nemeth superscript
        """
        result = ""
        
        # Base
        if node.children:
            result += self.render(node.children[0])
        
        # Superscript indicator + exponent
        result += self.SUPERSCRIPT_IND
        
        if len(node.children) > 1:
            result += self.render(node.children[1])
        
        # Note: Baseline indicator would be added contextually
        return result
    
    def _render_subscript(self, node: SemanticNode) -> str:
        """!
        @brief Render subscript.
        
        @details
        Uses subscript indicator ⠰ before the subscript.
        
        @param node Subscript node
        @return Nemeth subscript
        """
        result = ""
        
        # Base
        if node.children:
            result += self.render(node.children[0])
        
        # Subscript indicator + subscript
        result += self.SUBSCRIPT_IND
        
        if len(node.children) > 1:
            result += self.render(node.children[1])
        
        return result
    
    def _render_sqrt(self, node: SemanticNode) -> str:
        """!
        @brief Render square root.
        
        @details
        Uses ⠜ to open and ⠻ to close the radical.
        
        @param node Square root node
        @return Nemeth square root
        """
        result = self.SQRT_OPEN
        
        if node.children:
            result += self.render(node.children[0])
        
        result += self.SQRT_CLOSE
        return result
    
    def _render_nroot(self, node: SemanticNode) -> str:
        """!
        @brief Render n-th root.
        
        @param node N-th root node (index, radicand)
        @return Nemeth n-th root
        """
        result = ""
        
        # Index first (if present)
        if len(node.children) > 0:
            result += self.render(node.children[0])
        
        result += self.SQRT_OPEN
        
        # Radicand
        if len(node.children) > 1:
            result += self.render(node.children[1])
        
        result += self.SQRT_CLOSE
        return result
    
    def _render_sum(self, node: SemanticNode) -> str:
        """Render summation symbol."""
        return "⠠⠨⠎" + "".join(self.render(c) for c in node.children)
    
    def _render_integral(self, node: SemanticNode) -> str:
        """Render integral symbol."""
        return "⠮" + "".join(self.render(c) for c in node.children)
    
    def _render_function(self, node: SemanticNode) -> str:
        """Render function name (sin, cos, etc.)."""
        # Functions are written as regular text
        return "".join(self.LETTERS.get(c, c) for c in node.content.lower())
    
    def _render_text(self, node: SemanticNode) -> str:
        """Render text content."""
        result = ""
        for char in node.content.lower():
            if char in self.LETTERS:
                result += self.LETTERS[char]
            elif char in self.DIGITS:
                result += self.DIGITS[char]
            elif char == " ":
                result += "⠀"  # Braille space
            else:
                result += char
        return result
    
    def _render_default(self, node: SemanticNode) -> str:
        """Default rendering for unknown nodes."""
        if node.content:
            return self._render_text(SemanticNode(NodeType.TEXT, content=node.content))
        return "".join(self.render(c) for c in node.children)
