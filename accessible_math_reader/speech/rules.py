"""!
@file speech/rules.py
@brief Speech rule definitions for math verbalization.

@details
Provides configurable speech rules that transform semantic math nodes
into natural language. Supports multiple verbosity levels and is
designed for extensibility with custom rule sets.

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

from accessible_math_reader.core.semantic import SemanticNode, NodeType
from accessible_math_reader.core.renderer import BaseRenderer

if TYPE_CHECKING:
    from accessible_math_reader.config import Config


class VerbosityLevel(Enum):
    """!
    @brief Speech verbosity levels for math reading.
    
    @details
    - VERBOSE: Full structural announcements
      - "start fraction, a, over, b, end fraction"
    - CONCISE: Shorter but clear
      - "a over b"
    - SUPERBRIEF: Minimal for quick scanning
      - "fraction a b"
    """
    VERBOSE = "verbose"
    CONCISE = "concise"
    SUPERBRIEF = "superbrief"


class SpeechRuleSet:
    """!
    @brief A collection of speech rules for math verbalization.
    
    @details
    Defines how each node type should be spoken at different
    verbosity levels. Can be subclassed or extended with plugins.
    
    @section rules_example Example Usage
    @code{.py}
    rules = SpeechRuleSet()
    
    # Get phrase for fraction start
    start = rules.get_phrase("fraction_start", VerbosityLevel.VERBOSE)
    # Returns: "start fraction"
    @endcode
    """
    
    # Default phrases for different verbosity levels
    PHRASES = {
        "fraction_start": {
            VerbosityLevel.VERBOSE: "start fraction",
            VerbosityLevel.CONCISE: "",
            VerbosityLevel.SUPERBRIEF: "frac",
        },
        "fraction_over": {
            VerbosityLevel.VERBOSE: "over",
            VerbosityLevel.CONCISE: "over",
            VerbosityLevel.SUPERBRIEF: "",
        },
        "fraction_end": {
            VerbosityLevel.VERBOSE: "end fraction",
            VerbosityLevel.CONCISE: "",
            VerbosityLevel.SUPERBRIEF: "",
        },
        "superscript": {
            VerbosityLevel.VERBOSE: "to the power of",
            VerbosityLevel.CONCISE: "to the",
            VerbosityLevel.SUPERBRIEF: "exp",
        },
        "subscript": {
            VerbosityLevel.VERBOSE: "subscript",
            VerbosityLevel.CONCISE: "sub",
            VerbosityLevel.SUPERBRIEF: "sub",
        },
        "sqrt": {
            VerbosityLevel.VERBOSE: "square root of",
            VerbosityLevel.CONCISE: "square root of",
            VerbosityLevel.SUPERBRIEF: "sqrt",
        },
        "sqrt_end": {
            VerbosityLevel.VERBOSE: "end root",
            VerbosityLevel.CONCISE: "",
            VerbosityLevel.SUPERBRIEF: "",
        },
        "nroot": {
            VerbosityLevel.VERBOSE: "root of",
            VerbosityLevel.CONCISE: "root",
            VerbosityLevel.SUPERBRIEF: "root",
        },
        "sum": {
            VerbosityLevel.VERBOSE: "summation of",
            VerbosityLevel.CONCISE: "sum of",
            VerbosityLevel.SUPERBRIEF: "sum",
        },
        "integral": {
            VerbosityLevel.VERBOSE: "integral of",
            VerbosityLevel.CONCISE: "integral of",
            VerbosityLevel.SUPERBRIEF: "int",
        },
    }
    
    # Operator name mappings
    OPERATOR_NAMES = {
        "+": "plus",
        "-": "minus",
        "−": "minus",
        "×": "times",
        "·": "times",
        "÷": "divided by",
        "±": "plus or minus",
        "∓": "minus or plus",
        "(": "open paren",
        ")": "close paren",
        "[": "open bracket",
        "]": "close bracket",
    }
    
    # Relation name mappings
    RELATION_NAMES = {
        "=": "equals",
        "<": "less than",
        ">": "greater than",
        "≤": "less than or equal to",
        "≥": "greater than or equal to",
        "≠": "not equal to",
        "≈": "approximately equal to",
        "≡": "is identical to",
    }
    
    # Number name mappings for special numbers
    NUMBER_NAMES = {
        "∞": "infinity",
    }
    
    # Identifier name mappings (Greek letters, etc.)
    IDENTIFIER_NAMES = {
        "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta",
        "ε": "epsilon", "ζ": "zeta", "η": "eta", "θ": "theta",
        "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu",
        "ν": "nu", "ξ": "xi", "π": "pi", "ρ": "rho",
        "σ": "sigma", "τ": "tau", "υ": "upsilon", "φ": "phi",
        "χ": "chi", "ψ": "psi", "ω": "omega",
        "Α": "capital alpha", "Β": "capital beta", "Γ": "capital gamma",
        "Δ": "capital delta", "Θ": "capital theta", "Λ": "capital lambda",
        "Ξ": "capital xi", "Π": "capital pi", "Σ": "capital sigma",
        "Φ": "capital phi", "Ψ": "capital psi", "Ω": "capital omega",
        "∞": "infinity",
    }
    
    def get_phrase(self, key: str, verbosity: VerbosityLevel) -> str:
        """!
        @brief Get a phrase for a given key and verbosity level.
        
        @param key Phrase key (e.g., "fraction_start")
        @param verbosity Verbosity level
        @return The phrase, or empty string if not found
        """
        phrases = self.PHRASES.get(key, {})
        return phrases.get(verbosity, phrases.get(VerbosityLevel.VERBOSE, ""))
    
    def get_operator_name(self, operator: str) -> str:
        """!
        @brief Get spoken name for an operator.
        
        @param operator Operator symbol
        @return Spoken name
        """
        return self.OPERATOR_NAMES.get(operator, operator)
    
    def get_relation_name(self, relation: str) -> str:
        """!
        @brief Get spoken name for a relation.
        
        @param relation Relation symbol
        @return Spoken name
        """
        return self.RELATION_NAMES.get(relation, relation)
    
    def get_identifier_name(self, identifier: str) -> str:
        """!
        @brief Get spoken name for an identifier.
        
        @param identifier Identifier (may be Greek letter)
        @return Spoken name
        """
        return self.IDENTIFIER_NAMES.get(identifier, identifier)


class SpeechRenderer(BaseRenderer):
    """!
    @brief Renders semantic math trees to spoken text.
    
    @details
    Traverses the semantic tree and generates natural language
    descriptions suitable for text-to-speech or screen readers.
    
    @section speech_example Example Usage
    @code{.py}
    from accessible_math_reader import MathParser
    from accessible_math_reader.speech.rules import SpeechRenderer
    
    parser = MathParser()
    renderer = SpeechRenderer()
    
    tree = parser.parse(r"\\frac{a^2}{b}")
    speech = renderer.render(tree)
    # Output: "start fraction a to the power of 2 over b end fraction"
    @endcode
    """
    
    def __init__(self, config: Config | None = None) -> None:
        """!
        @brief Initialize the speech renderer.
        
        @param config Configuration object
        """
        super().__init__(config)
        self.rules = SpeechRuleSet()
        self._verbosity = self._get_verbosity()
    
    def _get_verbosity(self) -> VerbosityLevel:
        """Get verbosity level from config."""
        style = self.config.speech.style.value
        return VerbosityLevel(style)
    
    def render(self, node: SemanticNode) -> str:
        """!
        @brief Render a semantic node to speech text.
        
        @param node The node to render
        @return Spoken text representation
        """
        method = getattr(self, f"_render_{node.node_type.name.lower()}", None)
        if method:
            return method(node)
        return self._render_default(node)
    
    def _render_root(self, node: SemanticNode) -> str:
        """Render root node."""
        return self._join_parts(self.render(c) for c in node.children)
    
    def _render_group(self, node: SemanticNode) -> str:
        """Render group node."""
        return self._join_parts(self.render(c) for c in node.children)
    
    def _render_number(self, node: SemanticNode) -> str:
        """Render number."""
        return self.rules.NUMBER_NAMES.get(node.content, node.content)
    
    def _render_identifier(self, node: SemanticNode) -> str:
        """Render identifier."""
        return self.rules.get_identifier_name(node.content)
    
    def _render_operator(self, node: SemanticNode) -> str:
        """Render operator."""
        return self.rules.get_operator_name(node.content)
    
    def _render_relation(self, node: SemanticNode) -> str:
        """Render relation."""
        return self.rules.get_relation_name(node.content)
    
    def _render_function(self, node: SemanticNode) -> str:
        """Render function name."""
        return node.content
    
    def _render_fraction(self, node: SemanticNode) -> str:
        """!
        @brief Render fraction.
        
        @details
        Verbose: "start fraction [num] over [denom] end fraction"
        Concise: "[num] over [denom]"
        """
        parts = []
        
        start = self.rules.get_phrase("fraction_start", self._verbosity)
        if start:
            parts.append(start)
        
        if node.children:
            parts.append(self.render(node.children[0]))
        
        parts.append(self.rules.get_phrase("fraction_over", self._verbosity))
        
        if len(node.children) > 1:
            parts.append(self.render(node.children[1]))
        
        end = self.rules.get_phrase("fraction_end", self._verbosity)
        if end:
            parts.append(end)
        
        return self._join_parts(parts)
    
    def _render_superscript(self, node: SemanticNode) -> str:
        """!
        @brief Render superscript/exponent.
        
        @details
        Verbose: "[base] to the power of [exp]"
        """
        parts = []
        
        if node.children:
            parts.append(self.render(node.children[0]))
        
        parts.append(self.rules.get_phrase("superscript", self._verbosity))
        
        if len(node.children) > 1:
            parts.append(self.render(node.children[1]))
        
        return self._join_parts(parts)
    
    def _render_subscript(self, node: SemanticNode) -> str:
        """!
        @brief Render subscript.
        
        @details
        Verbose: "[base] subscript [sub]"
        """
        parts = []
        
        if node.children:
            parts.append(self.render(node.children[0]))
        
        parts.append(self.rules.get_phrase("subscript", self._verbosity))
        
        if len(node.children) > 1:
            parts.append(self.render(node.children[1]))
        
        return self._join_parts(parts)
    
    def _render_sqrt(self, node: SemanticNode) -> str:
        """!
        @brief Render square root.
        """
        parts = [self.rules.get_phrase("sqrt", self._verbosity)]
        
        if node.children:
            parts.append(self.render(node.children[0]))
        
        end = self.rules.get_phrase("sqrt_end", self._verbosity)
        if end:
            parts.append(end)
        
        return self._join_parts(parts)
    
    def _render_nroot(self, node: SemanticNode) -> str:
        """!
        @brief Render n-th root.
        """
        parts = []
        
        # Index comes first
        if len(node.children) > 0:
            parts.append(self.render(node.children[0]))
        
        parts.append(self.rules.get_phrase("nroot", self._verbosity))
        
        # Radicand
        if len(node.children) > 1:
            parts.append(self.render(node.children[1]))
        
        return self._join_parts(parts)
    
    def _render_sum(self, node: SemanticNode) -> str:
        """Render summation."""
        parts = [self.rules.get_phrase("sum", self._verbosity)]
        parts.extend(self.render(c) for c in node.children)
        return self._join_parts(parts)
    
    def _render_integral(self, node: SemanticNode) -> str:
        """Render integral."""
        parts = [self.rules.get_phrase("integral", self._verbosity)]
        parts.extend(self.render(c) for c in node.children)
        return self._join_parts(parts)
    
    def _render_text(self, node: SemanticNode) -> str:
        """Render text content."""
        return node.content
    
    def _render_default(self, node: SemanticNode) -> str:
        """Default rendering for unknown node types."""
        if node.content:
            return node.content
        return self._join_parts(self.render(c) for c in node.children)
    
    def _join_parts(self, parts) -> str:
        """Join parts, filtering empty strings."""
        return " ".join(p for p in parts if p)
