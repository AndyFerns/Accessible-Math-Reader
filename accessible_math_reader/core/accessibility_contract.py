"""!
@file core/accessibility_contract.py
@brief Accessibility contracts and protocols for screen reader integration.

@details
Defines TypedDict protocols, validation functions, and contracts that
ensure the Accessible Math Reader provides deterministic, accessible output
for screen readers and assistive technologies.

This module establishes the "accessibility contract" - guaranteed behaviors
and data structures that frontends and AT can rely on.

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypedDict, Protocol, Optional, Any
from typing_extensions import NotRequired


# ============================================================================
# Accessibility Metadata Types
# ============================================================================

class AccessibilityMetadata(TypedDict):
    """!
    @brief Structured accessibility metadata for semantic nodes.
    
    @details
    This TypedDict defines the contract for accessibility information
    attached to each semantic node. Screen readers and ARIA renderers
    can reliably expect these fields.
    
    Fields:
    - spoken_text: Natural language description for TTS
    - aria_role: ARIA role attribute value
    - aria_label: Short accessible label
    - description: Long description for aria-describedby
    - navigation_hint: Keyboard shortcut hint
    - aria_roledescription: Custom role description
    """
    spoken_text: NotRequired[str]              # Natural language for TTS
    aria_role: NotRequired[str]                 # ARIA role (e.g., "math", "group")
    aria_label: NotRequired[str]                # Short label
    description: NotRequired[str]               # Long description
    navigation_hint: NotRequired[str]           # e.g., "Press Enter to explore"
    aria_roledescription: NotRequired[str]      # e.g., "fraction", "exponent"


class ARIAAttributes(TypedDict):
    """!
    @brief ARIA attributes for HTML rendering.
    
    @details
    Standardized ARIA attributes that renderers should apply to DOM elements.
    """
    id: str                                     # Unique element ID
    role: str                                   # ARIA role
    aria_label: NotRequired[str]                # Accessible label
    aria_describedby: NotRequired[str]          # ID of description element
    aria_roledescription: NotRequired[str]      # Custom role description
    aria_owns: NotRequired[str]                 # Space-separated child IDs
    tabindex: NotRequired[str]                  # Tab index (-1, 0, 1+)
    aria_live: NotRequired[str]                 # Live region politeness
    aria_atomic: NotRequired[str]               # Read entire region or changes only


class NavigationCommand(Enum):
    """!
    @brief Navigation commands for keyboard interaction.
    
    @details
    Defines the set of navigation actions users can perform
    when exploring mathematical expressions.
    """
    ENTER = auto()          # Drill down into current element
    EXIT = auto()           # Move up to parent
    NEXT = auto()           # Move to next sibling
    PREVIOUS = auto()       # Move to previous sibling
    FIRST = auto()          # Jump to first sibling
    LAST = auto()           # Jump to last sibling
    WHERE_AM_I = auto()     # Announce current position
    HELP = auto()           # Show keyboard shortcuts


# ============================================================================
# Navigation State Protocol
# ============================================================================

class NavigationState(Protocol):
    """!
    @brief Protocol for navigation state tracking.
    
    @details
    Defines the interface that navigation implementations must provide.
    Ensures consistent navigation behavior across different modes.
    """
    
    def get_current_node_id(self) -> str:
        """Get the ID of the currently focused node."""
        ...
    
    def get_announcement(self) -> str:
        """Get the text to announce for the current position."""
        ...
    
    def execute_command(self, command: NavigationCommand) -> bool:
        """
        Execute a navigation command.
        Returns True if successful, False otherwise.
        """
        ...
    
    def get_breadcrumb(self) -> list[str]:
        """Get breadcrumb trail from root to current node."""
        ...


# ============================================================================
# Screen Reader Output
# ============================================================================

@dataclass
class ScreenReaderOutput:
    """!
    @brief Complete output package for screen readers.
    
    @details
    Bundles all information needed for accessible math presentation:
    - HTML with ARIA attributes
    - Plain text description
    - Speech text (with prosody hints)
    - Braille output
    - Navigation metadata
    """
    # Main content
    aria_html: str                              # HTML with full ARIA markup
    plain_text: str                             # Simplified text description
    speech_text: str                            # Optimized for TTS
    braille_text: str                           # Nemeth or UEB Braille
    
    # Metadata
    node_structure: dict[str, Any]              # JSON representation of tree
    navigation_map: dict[str, str]              # node_id -> description
    keyboard_shortcuts: dict[str, str]          # command -> key binding
    
    # Configuration used
    config_snapshot: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Accessibility Contract
# ============================================================================

class AccessibilityContract:
    """!
    @brief Abstract base class defining accessibility guarantees.
    
    @details
    Implementations of this contract guarantee:
    1. Deterministic output (same input -> same output)
    2. Complete ARIA metadata for all nodes
    3. Keyboard-navigable structure
    4. Screen reader compatible announcements
    5. Error handling with accessible fallbacks
    """
    
    @staticmethod
    def validate_node_accessibility(node: Any) -> tuple[bool, list[str]]:
        """!
        @brief Validate that a semantic node meets accessibility requirements.
        
        @param node SemanticNode to validate
        @return Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for node_id
        if not hasattr(node, 'node_id') or not node.node_id:
            issues.append("Missing node_id")
        
        # Check for accessibility_metadata
        if not hasattr(node, 'accessibility_metadata'):
            issues.append("Missing accessibility_metadata attribute")
        else:
            metadata = node.accessibility_metadata
            
            # Warn if no spoken text
            if 'spoken_text' not in metadata and node.is_leaf:
                issues.append("Leaf node missing spoken_text")
            
            # Warn if no ARIA role
            if 'aria_role' not in metadata:
                issues.append("Missing aria_role")
        
        return (len(issues) == 0, issues)
    
    @staticmethod
    def validate_aria_attributes(attrs: dict[str, str]) -> tuple[bool, list[str]]:
        """!
        @brief Validate ARIA attributes for correctness.
        
        @param attrs Dictionary of ARIA attributes
        @return Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Required attributes
        if 'id' not in attrs or not attrs['id']:
            issues.append("Missing required 'id' attribute")
        
        if 'role' not in attrs or not attrs['role']:
            issues.append("Missing required 'role' attribute")
        
        # Validate role values (basic check)
        valid_roles = {
            'math', 'group', 'term', 'region', 'application',
            'article', 'button', 'toolbar', 'status'
        }
        if 'role' in attrs and attrs['role'] not in valid_roles:
            # Allow custom roles, but warn
            pass  # Could add warning system here
        
        # Validate aria-live values
        if 'aria-live' in attrs:
            valid_politeness = {'off', 'polite', 'assertive'}
            if attrs['aria-live'] not in valid_politeness:
                issues.append(f"Invalid aria-live value: {attrs['aria-live']}")
        
        return (len(issues) == 0, issues)
    
    @staticmethod
    def ensure_deterministic_ids(node: Any, prefix: str = "math") -> None:
        """!
        @brief Ensure node IDs are deterministic based on tree structure.
        
        @details
        Replaces random UUIDs with deterministic IDs based on position
        in the tree. Useful for testing and consistent focus management.
        
        @param node Root semantic node
        @param prefix Prefix for generated IDs
        """
        def assign_ids(n: Any, path: list[int]) -> None:
            # Generate deterministic ID from path
            # e.g., "math-0-1-2" for root -> first child -> second child -> third child
            id_suffix = "-".join(map(str, path)) if path else "root"
            n.node_id = f"{prefix}-{id_suffix}"
            
            # Recursively assign to children
            for i, child in enumerate(n.children):
                assign_ids(child, path + [i])
        
        assign_ids(node, [])


# ============================================================================
# Validation Functions
# ============================================================================

def validate_screen_reader_output(output: ScreenReaderOutput) -> tuple[bool, list[str]]:
    """!
    @brief Validate a complete screen reader output package.
    
    @param output ScreenReaderOutput to validate
    @return Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    if not output.aria_html:
        issues.append("Missing ARIA HTML output")
    
    if not output.plain_text:
        issues.append("Missing plain text output")
    
    if not output.speech_text:
        issues.append("Missing speech text output")
    
    if not output.braille_text:
        issues.append("Missing Braille output")
    
    # Validate structure
    if not output.node_structure:
        issues.append("Missing node structure")
    elif 'type' not in output.node_structure:
        issues.append("Node structure missing 'type' field")
    
    return (len(issues) == 0, issues)


def create_fallback_accessibility_metadata(node_type: str, content: str) -> AccessibilityMetadata:
    """!
    @brief Create minimal accessibility metadata as a fallback.
    
    @details
    Used when accessibility metadata is missing or incomplete.
    Provides basic but functional accessibility information.
    
    @param node_type The type of the node
    @param content The content of the node
    @return Minimal AccessibilityMetadata
    """
    return {
        'spoken_text': f"{node_type}: {content}" if content else node_type,
        'aria_role': 'group',
        'aria_label': content or node_type,
    }
