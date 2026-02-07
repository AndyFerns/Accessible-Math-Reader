"""!
@file core/aria_renderer.py
@brief Render semantic math trees as accessible HTML with full ARIA support.

@details
Generates semantic HTML with:
- Proper ARIA roles and attributes
- Parent-child relationships via aria-owns
- Descriptions via aria-describedby
- Roving tabindex for keyboard navigation
- Hidden description elements

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from html import escape

from accessible_math_reader.core.semantic import SemanticNode, NodeType

if TYPE_CHECKING:
    from accessible_math_reader.config import Config


# ============================================================================
# ARIA Renderer
# ============================================================================

def render_to_aria_html(
    node: SemanticNode,
    config: Optional[Config] = None,
    initial_focus: bool = True
) -> str:
    """!
    @brief Render a semantic tree to accessible HTML with ARIA.
    
    @details
    Generates semantic HTML with full ARIA markup for screen readers:
    - Proper ARIA roles for math elements
    - aria-label for concise descriptions
    - aria-describedby for detailed descriptions
    - aria-owns for structural relationships
    - Roving tabindex for keyboard navigation
    
    @param node Root semantic node to render
    @param config Accessibility configuration
    @param initial_focus Whether this node should have initial focus (tabindex=0)
    @return HTML string with full ARIA markup
    """
    from accessible_math_reader.config import Config
    config = config or Config()
    
    # Start building HTML
    html_parts = []
    
    # Add wrapper div with role="math"
    html_parts.append(f'<div role="math" aria-label="Mathematical expression" id="{node.node_id}-container">')
    
    # Render the node tree
    html_parts.append(_render_node(node, config, initial_focus))
    
    # Close wrapper
    html_parts.append('</div>')
    
    return ''.join(html_parts)


def _render_node(node: SemanticNode, config: Config, is_focused: bool = False, depth: int = 0) -> str:
    """!
    @brief Recursively render a node with ARIA attributes.
    
    @param node Node to render
    @param config Configuration
    @param is_focused Whether this node should receive initial focus
    @param depth Current depth in tree (for indentation in output)
    @return HTML string for this node and its children
    """
    parts = []
    
    # Get ARIA attributes from node
    attrs = node.get_aria_attributes()
    
    # Override tabindex based on focus state
    attrs['tabindex'] = '0' if is_focused else '-1'
    
    # Add data attribute for node type (useful for CSS styling)
    attrs['data-math-type'] = node.node_type.name.lower()
    
    # Build attribute string
    attr_str = ' '.join(f'{k}="{escape(str(v))}"' for k, v in attrs.items())
    
    # Choose element type based on node
    elem_type = 'div' if node.children else 'span'
    
    # Open tag
    parts.append(f'<{elem_type} {attr_str}>')
    
    # Add visible content for leaf nodes
    if node.is_leaf and node.content:
        parts.append(escape(node.content))
    
    # Recursively render children
    for i, child in enumerate(node.children):
        # Only first child of root gets initial focus
        child_focused = is_focused and i == 0 and depth == 0
        parts.append(_render_node(child, config, child_focused, depth + 1))
    
    # Close tag
    parts.append(f'</{elem_type}>')
    
    # Add hidden description element if description exists
    if 'description' in node.accessibility_metadata:
        desc_id = f"{node.node_id}-desc"
        desc_text = escape(node.accessibility_metadata['description'])
        parts.append(f'<div id="{desc_id}" class="sr-only" hidden>{desc_text}</div>')
    
    return ''.join(parts)


def render_with_focus_indicator(
    node: SemanticNode,
    config: Optional[Config] = None,
    focused_node_id: Optional[str] = None
) -> str:
    """!
    @brief Render HTML with specific node focused.
    
    @details
    Useful for updating the DOM after navigation to show
    which element currently has focus.
    
    @param node Root node
    @param config Configuration
    @param focused_node_id ID of node that should be focused
    @return HTML with correct tabindex values
    """
    from accessible_math_reader.config import Config
    config = config or Config()
    
    # Similar to render_to_aria_html but with dynamic focus
    def render_with_focus(n: SemanticNode, depth: int = 0) -> str:
        is_focused = n.node_id == focused_node_id
        return _render_node(n, config, is_focused, depth)
    
    html_parts = []
    html_parts.append(f'<div role="math" aria-label="Mathematical expression" id="{node.node_id}-container">')
    html_parts.append(render_with_focus(node))
    html_parts.append('</div>')
    
    return ''.join(html_parts)


def generate_live_region_html() -> str:
    """!
    @brief Generate ARIA live region for announcements.
    
    @details
    Creates an ARIA live region that screen readers will announce
    when updated. Should be included once in the page.
    
    @return HTML for live region
    """
    return (
        '<div '
        'id="math-announcements" '
        'role="status" '
        'aria-live="polite" '
        'aria-atomic="true" '
        'class="sr-only"'
        '></div>'
    )


def generate_keyboard_shortcuts_dialog(shortcuts: dict[str, str]) -> str:
    """!
    @brief Generate HTML for keyboard shortcuts help dialog.
    
    @param shortcuts Dictionary mapping descriptions to key bindings
    @return HTML for dialog
    """
    parts = []
    
    parts.append('<dialog id="keyboard-shortcuts-dialog" aria-labelledby="shortcuts-title">')
    parts.append('  <h2 id="shortcuts-title">Keyboard Shortcuts</h2>')
    parts.append('  <table>')
    parts.append('    <thead>')
    parts.append('      <tr><th>Action</th><th>Key</th></tr>')
    parts.append('    </thead>')
    parts.append('    <tbody>')
    
    for action, key in shortcuts.items():
        parts.append(f'      <tr><td>{escape(action)}</td><td><kbd>{escape(key)}</kbd></td></tr>')
    
    parts.append('    </tbody>')
    parts.append('  </table>')
    parts.append('  <button id="close-shortcuts" autofocus>Close</button>')
    parts.append('</dialog>')
    
    return '\n'.join(parts)


# ============================================================================
# Utility Functions
# ============================================================================

def add_screen_reader_only_class_css() -> str:
    """!
    @brief Generate CSS for screen-reader-only elements.
    
    @return CSS string
    """
    return """
/* Screen reader only - visually hidden but accessible */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
"""


def add_focus_indicator_css(style: str = "default") -> str:
    """!
    @brief Generate CSS for focus indicators.
    
    @param style Style name from config
    @return CSS string
    """
    if style == "high-contrast":
        return """
/* High contrast focus indicator */
[role="math"] [tabindex="0"] {
    outline: 3px solid #000;
    outline-offset: 3px;
    background-color: #ff0 !important;
    color: #000 !important;
}
"""
    else:  # default
        return """
/* Default focus indicator */
[role="math"] [tabindex="0"] {
    background-color: rgba(0, 120, 212, 0.15);
    outline: 2px solid #0078d4;
    outline-offset: 2px;
    border-radius: 2px;
}

/* Visible focus for keyboard navigation */
[role="math"] *:focus {
    outline: 3px solid #0078d4;
    outline-offset: 2px;
}
"""
