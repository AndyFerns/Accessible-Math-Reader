"""!
@file core/semantic.py
@brief Semantic representation of mathematical expressions.

@details
Defines the AST (Abstract Syntax Tree) structure for representing math
in a format-agnostic way. This intermediate representation enables:
- Consistent processing regardless of input format (LaTeX, MathML)
- Step-by-step navigation through sub-expressions
- Targeted speech/Braille generation

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Iterator, Any


class NodeType(Enum):
    """!
    @brief Types of mathematical semantic nodes.
    
    @details
    Each node type represents a distinct mathematical concept that
    may require specific handling for speech or Braille output.
    """
    # Structural
    ROOT = auto()           ##< Root of the expression tree
    GROUP = auto()          ##< Grouping (parentheses, brackets)
    
    # Numbers and identifiers
    NUMBER = auto()         ##< Numeric literal (e.g., 42, 3.14)
    IDENTIFIER = auto()     ##< Variable or constant (e.g., x, pi)
    
    # Operations
    FRACTION = auto()       ##< Fraction (numerator/denominator)
    SUPERSCRIPT = auto()    ##< Superscript/exponent
    SUBSCRIPT = auto()      ##< Subscript
    SQRT = auto()           ##< Square root
    NROOT = auto()          ##< N-th root
    
    # Operators
    OPERATOR = auto()       ##< Binary/unary operator (+, -, *, etc.)
    RELATION = auto()       ##< Relational operator (=, <, >, etc.)
    
    # Functions
    FUNCTION = auto()       ##< Named function (sin, cos, log, etc.)
    
    # Calculus
    SUM = auto()            ##< Summation
    PRODUCT = auto()        ##< Product notation
    INTEGRAL = auto()       ##< Integral
    LIMIT = auto()          ##< Limit
    
    # Matrices
    MATRIX = auto()         ##< Matrix
    MATRIX_ROW = auto()     ##< Matrix row
    
    # Special
    TEXT = auto()           ##< Text content
    SPACE = auto()          ##< Whitespace


@dataclass
class SemanticNode:
    """!
    @brief A node in the mathematical expression tree.
    
    @details
    Represents a single component of a mathematical expression with
    its type, content, and children. Supports tree traversal for
    step-by-step navigation.
    
    @section node_example Example Usage
    @code{.py}
    # Create a fraction: a/b
    fraction = SemanticNode(
        node_type=NodeType.FRACTION,
        children=[
            SemanticNode(NodeType.IDENTIFIER, content="a"),
            SemanticNode(NodeType.IDENTIFIER, content="b")
        ]
    )
    
    # Navigate children
    for child in fraction:
        print(child.content)
    @endcode
    
    @param node_type The type of mathematical construct
    @param content Text content for leaf nodes (numbers, identifiers)
    @param children Child nodes (e.g., numerator/denominator for fractions)
    @param parent Reference to parent node (set automatically)
    @param metadata Additional data (e.g., original LaTeX, position info)
    @param node_id Unique stable identifier for ARIA and navigation (auto-generated)
    @param accessibility_metadata Structured metadata for screen readers and ARIA
    """
    node_type: NodeType
    content: str = ""
    children: list[SemanticNode] = field(default_factory=list)
    parent: Optional[SemanticNode] = field(default=None, repr=False)
    metadata: dict = field(default_factory=dict)
    
    # === ACCESSIBILITY ENHANCEMENTS ===
    # Stable unique ID for ARIA relationships and DOM manipulation
    # This ID persists across re-renders to maintain focus and state
    node_id: str = field(default_factory=lambda: f"math-node-{uuid.uuid4().hex[:8]}")
    
    # Accessibility metadata for screen reader integration
    # Contains: spoken_text, aria_role, aria_label, description, navigation_hint
    accessibility_metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """!
        @brief Set parent references for all children after initialization.
        """
        for child in self.children:
            child.parent = self
    
    def add_child(self, child: SemanticNode) -> None:
        """!
        @brief Add a child node and set its parent reference.
        
        @param child The child node to add
        """
        child.parent = self
        self.children.append(child)
    
    def __iter__(self) -> Iterator[SemanticNode]:
        """!
        @brief Iterate over child nodes.
        
        @return Iterator over children
        """
        return iter(self.children)
    
    def __len__(self) -> int:
        """!
        @brief Get the number of children.
        
        @return Number of child nodes
        """
        return len(self.children)
    
    def __getitem__(self, index: int) -> SemanticNode:
        """!
        @brief Get a child by index.
        
        @param index Index of the child
        @return The child node at the given index
        """
        return self.children[index]
    
    @property
    def is_leaf(self) -> bool:
        """!
        @brief Check if this is a leaf node (no children).
        
        @return True if node has no children
        """
        return len(self.children) == 0
    
    @property
    def depth(self) -> int:
        """!
        @brief Calculate the depth of this node in the tree.
        
        @return Depth (0 for root)
        """
        d = 0
        node = self
        while node.parent is not None:
            d += 1
            node = node.parent
        return d
    
    def walk(self) -> Iterator[SemanticNode]:
        """!
        @brief Perform depth-first traversal of the subtree.
        
        @details
        Yields each node in the subtree rooted at this node,
        in pre-order (parent before children).
        
        @return Iterator over all nodes in subtree
        """
        yield self
        for child in self.children:
            yield from child.walk()
    
    def walk_leaves(self) -> Iterator[SemanticNode]:
        """!
        @brief Iterate over only the leaf nodes in subtree.
        
        @return Iterator over leaf nodes
        """
        for node in self.walk():
            if node.is_leaf:
                yield node
    
    def get_navigable_children(self) -> list[SemanticNode]:
        """!
        @brief Get children that should be navigable in step-by-step mode.
        
        @details
        Some node types (like GROUP) may not be meaningful navigation
        targets themselves, so this filters to significant children.
        
        @return List of navigable child nodes
        """
        navigable = []
        for child in self.children:
            if child.node_type in (NodeType.GROUP, NodeType.ROOT):
                # Flatten groups - navigate their children directly
                navigable.extend(child.get_navigable_children())
            else:
                navigable.append(child)
        return navigable
    
    def to_dict(self) -> dict:
        """!
        @brief Convert node to dictionary (for JSON serialization).
        
        @details
        Includes accessibility metadata for screen reader integration
        and ARIA attribute generation.
        
        @return Dictionary representation of the node tree
        """
        return {
            "type": self.node_type.name,
            "content": self.content,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
            # Accessibility enhancements for screen readers
            "node_id": self.node_id,
            "accessibility": self.accessibility_metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> SemanticNode:
        """!
        @brief Create a node from a dictionary.
        
        @param data Dictionary representation
        @return SemanticNode instance
        """
        node = cls(
            node_type=NodeType[data["type"]],
            content=data.get("content", ""),
            children=[cls.from_dict(c) for c in data.get("children", [])],
            metadata=data.get("metadata", {}),
        )
        
        # Restore accessibility data if present
        if "node_id" in data:
            node.node_id = data["node_id"]
        if "accessibility" in data:
            node.accessibility_metadata = data["accessibility"]
        
        return node
    
    def get_aria_attributes(self) -> dict[str, str]:
        """!
        @brief Get ARIA attributes for this node.
        
        @details
        Generates appropriate ARIA attributes based on node type and
        accessibility metadata. Used for rendering accessible HTML.
        
        @return Dictionary of ARIA attribute names and values
        """
        attrs = {
            "id": self.node_id,
            "role": self.accessibility_metadata.get("aria_role", "group"),
        }
        
        # Add aria-label if available
        if "aria_label" in self.accessibility_metadata:
            attrs["aria-label"] = self.accessibility_metadata["aria_label"]
        
        # Add aria-describedby if description exists
        if "description" in self.accessibility_metadata:
            attrs["aria-describedby"] = f"{self.node_id}-desc"
        
        # Add aria-roledescription for math-specific roles
        if "aria_roledescription" in self.accessibility_metadata:
            attrs["aria-roledescription"] = self.accessibility_metadata["aria_roledescription"]
        
        # Add aria-owns for parent-child relationships
        if self.children:
            child_ids = [child.node_id for child in self.children]
            attrs["aria-owns"] = " ".join(child_ids)
        
        return attrs
    
    def set_accessibility_metadata(
        self,
        spoken_text: Optional[str] = None,
        aria_role: Optional[str] = None,
        aria_label: Optional[str] = None,
        description: Optional[str] = None,
        navigation_hint: Optional[str] = None,
        aria_roledescription: Optional[str] = None,
    ) -> None:
        """!
        @brief Set accessibility metadata for this node.
        
        @details
        Convenience method to populate accessibility metadata fields.
        Used by renderers to add screen reader-friendly information.
        
        @param spoken_text Natural language description for speech output
        @param aria_role ARIA role (e.g., "math", "group", "term")
        @param aria_label Short accessible label
        @param description Long description for aria-describedby
        @param navigation_hint Keyboard navigation hint
        @param aria_roledescription Custom role description for math concepts
        """
        if spoken_text is not None:
            self.accessibility_metadata["spoken_text"] = spoken_text
        if aria_role is not None:
            self.accessibility_metadata["aria_role"] = aria_role
        if aria_label is not None:
            self.accessibility_metadata["aria_label"] = aria_label
        if description is not None:
            self.accessibility_metadata["description"] = description
        if navigation_hint is not None:
            self.accessibility_metadata["navigation_hint"] = navigation_hint
        if aria_roledescription is not None:
            self.accessibility_metadata["aria_roledescription"] = aria_roledescription


class MathNavigator:
    """!
    @brief Navigator for step-by-step exploration of math expressions.
    
    @details
    Provides keyboard-navigable traversal through a semantic tree,
    enabling screen reader users to explore equations piece by piece.
    
    @section nav_example Example Usage
    @code{.py}
    nav = MathNavigator(semantic_tree)
    
    # Get description of current position
    print(nav.current_description())  # "fraction, 2 parts"
    
    # Move into fraction
    nav.enter()
    print(nav.current_description())  # "numerator: a"
    
    # Move to denominator
    nav.next()
    print(nav.current_description())  # "denominator: b"
    @endcode
    """
    
    def __init__(self, root: SemanticNode) -> None:
        """!
        @brief Initialize navigator at the root of an expression.
        
        @param root The root node of the semantic tree
        """
        self._root = root
        self._current = root
        self._position_stack: list[int] = []
        self._sibling_index = 0
    
    @property
    def current(self) -> SemanticNode:
        """!
        @brief Get the currently focused node.
        
        @return Current node
        """
        return self._current
    
    def enter(self) -> bool:
        """!
        @brief Move into the current node's children.
        
        @return True if successful, False if no children
        """
        navigable = self._current.get_navigable_children()
        if not navigable:
            return False
        
        self._position_stack.append(self._sibling_index)
        self._sibling_index = 0
        self._current = navigable[0]
        return True
    
    def exit(self) -> bool:
        """!
        @brief Move up to the parent node.
        
        @return True if successful, False if at root
        """
        if self._current.parent is None or not self._position_stack:
            return False
        
        self._current = self._current.parent
        self._sibling_index = self._position_stack.pop()
        return True
    
    def next(self) -> bool:
        """!
        @brief Move to the next sibling.
        
        @return True if successful, False if at last sibling
        """
        if self._current.parent is None:
            return False
        
        siblings = self._current.parent.get_navigable_children()
        if self._sibling_index >= len(siblings) - 1:
            return False
        
        self._sibling_index += 1
        self._current = siblings[self._sibling_index]
        return True
    
    def previous(self) -> bool:
        """!
        @brief Move to the previous sibling.
        
        @return True if successful, False if at first sibling
        """
        if self._current.parent is None or self._sibling_index <= 0:
            return False
        
        self._sibling_index -= 1
        siblings = self._current.parent.get_navigable_children()
        self._current = siblings[self._sibling_index]
        return True
    
    def reset(self) -> None:
        """!
        @brief Reset navigation to the root.
        """
        self._current = self._root
        self._position_stack.clear()
        self._sibling_index = 0
    
    def get_path(self) -> list[SemanticNode]:
        """!
        @brief Get the path from root to current node.
        
        @return List of nodes from root to current (inclusive)
        """
        path = []
        node = self._current
        while node is not None:
            path.append(node)
            node = node.parent
        return list(reversed(path))
