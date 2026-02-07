"""!
@file core/renderer.py
@brief Renders semantic math trees to various output formats.

@details
Provides base rendering infrastructure and format-agnostic traversal
for converting semantic representations to speech text, Braille, etc.

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from accessible_math_reader.core.semantic import SemanticNode, NodeType

if TYPE_CHECKING:
    from accessible_math_reader.config import Config


class BaseRenderer(ABC):
    """!
    @brief Abstract base class for math renderers.
    
    @details
    Defines the interface for converting semantic nodes to output strings.
    Subclasses implement format-specific rendering logic.
    """
    
    def __init__(self, config: Config | None = None) -> None:
        """!
        @brief Initialize renderer with configuration.
        
        @param config Configuration object (uses defaults if None)
        """
        if config is None:
            from accessible_math_reader.config import Config
            config = Config()
        self.config = config
    
    @abstractmethod
    def render(self, node: SemanticNode) -> str:
        """!
        @brief Render a semantic node to output format.
        
        @param node The semantic node to render
        @return Rendered string
        """
        pass
    
    def render_children(self, node: SemanticNode, separator: str = " ") -> str:
        """!
        @brief Render all children of a node with a separator.
        
        @param node Parent node
        @param separator String between rendered children
        @return Combined rendered string
        """
        return separator.join(self.render(child) for child in node.children)


class MathRenderer:
    """!
    @brief High-level renderer coordinating speech and Braille output.
    
    @details
    Provides a unified interface for rendering math to multiple formats
    with consistent configuration.
    
    @section renderer_example Example Usage
    @code{.py}
    from accessible_math_reader import MathParser, MathRenderer
    
    parser = MathParser()
    renderer = MathRenderer()
    
    tree = parser.parse(r"\\frac{a}{b}")
    
    speech = renderer.to_speech(tree)
    braille = renderer.to_braille(tree)
    @endcode
    """
    
    def __init__(self, config: Config | None = None) -> None:
        """!
        @brief Initialize the math renderer.
        
        @param config Configuration object
        """
        if config is None:
            from accessible_math_reader.config import Config
            config = Config()
        self.config = config
        
        # Lazy-load renderers
        self._speech_renderer = None
        self._braille_renderer = None
    
    def to_speech(self, node: SemanticNode) -> str:
        """!
        @brief Render semantic tree to speech text.
        
        @param node Root of semantic tree
        @return Spoken text representation
        """
        from accessible_math_reader.speech.rules import SpeechRenderer
        
        if self._speech_renderer is None:
            self._speech_renderer = SpeechRenderer(self.config)
        
        return self._speech_renderer.render(node)
    
    def to_braille(self, node: SemanticNode, notation: str = "nemeth") -> str:
        """!
        @brief Render semantic tree to Braille.
        
        @param node Root of semantic tree
        @param notation Braille notation ("nemeth" or "ueb")
        @return Braille string
        """
        if notation == "nemeth":
            from accessible_math_reader.braille.nemeth import NemethConverter
            converter = NemethConverter(self.config)
        else:
            from accessible_math_reader.braille.ueb import UEBConverter
            converter = UEBConverter(self.config)
        
        return converter.render(node)
    
    def to_simple_text(self, node: SemanticNode) -> str:
        """!
        @brief Render to simple text (for basic display/debugging).
        
        @param node Root of semantic tree
        @return Simple text representation
        """
        return self._render_simple(node)
    
    def _render_simple(self, node: SemanticNode) -> str:
        """Recursive simple text rendering."""
        if node.node_type == NodeType.ROOT:
            return " ".join(self._render_simple(c) for c in node.children)
        
        elif node.node_type == NodeType.GROUP:
            content = " ".join(self._render_simple(c) for c in node.children)
            return f"({content})" if len(node.children) > 1 else content
        
        elif node.node_type == NodeType.FRACTION:
            num = self._render_simple(node.children[0]) if node.children else ""
            denom = self._render_simple(node.children[1]) if len(node.children) > 1 else ""
            return f"({num})/({denom})"
        
        elif node.node_type == NodeType.SUPERSCRIPT:
            base = self._render_simple(node.children[0]) if node.children else ""
            exp = self._render_simple(node.children[1]) if len(node.children) > 1 else ""
            return f"{base}^{exp}"
        
        elif node.node_type == NodeType.SUBSCRIPT:
            base = self._render_simple(node.children[0]) if node.children else ""
            sub = self._render_simple(node.children[1]) if len(node.children) > 1 else ""
            return f"{base}_{sub}"
        
        elif node.node_type == NodeType.SQRT:
            radicand = self._render_simple(node.children[0]) if node.children else ""
            return f"√({radicand})"
        
        elif node.node_type in (NodeType.NUMBER, NodeType.IDENTIFIER, 
                                NodeType.OPERATOR, NodeType.RELATION,
                                NodeType.TEXT, NodeType.FUNCTION):
            return node.content
        
        else:
            return " ".join(self._render_simple(c) for c in node.children)
