"""!
@file core/aria_navigator.py
@brief ARIA-enhanced navigator for accessible math exploration.

@details
Extends the basic MathNavigator with ARIA support, mode switching
(Browse/Explore/Verbose Learning), and screen reader announcements.
Implements the roving tabindex pattern and keyboard navigation.

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

from accessible_math_reader.core.semantic import MathNavigator, SemanticNode, NodeType
from accessible_math_reader.config import NavigationMode

if TYPE_CHECKING:
    from accessible_math_reader.config import Config


# ============================================================================
# Focus Management
# ============================================================================

class FocusManager:
    """!
    @brief Manages focus state and roving tabindex for math navigation.
    
    @details
    Implements the WAI-ARIA roving tabindex pattern where only one element
    is focusable at a time (tabindex=0), while others remain in the tab
    order but skip automatic focus (tabindex=-1).
    
    This ensures keyboard users can navigate math expressions without
    getting trapped or losing context.
    """
    
    def __init__(self) -> None:
        """!
        @brief Initialize the focus manager.
        """
        self._focused_node_id: Optional[str] = None
        self._focus_history: list[str] = []
    
    def set_focus(self, node_id: str) -> dict[str, str]:
        """!
        @brief Set focus to a specific node.
        
        @details
        Updates the focused node and returns the tabindex updates
        needed for all affected nodes.
        
        @param node_id ID of the node to focus
        @return Dictionary mapping node IDs to new tabindex values
        """
        # Save previous focus to history
        if self._focused_node_id:
            self._focus_history.append(self._focused_node_id)
        
        # Update focused node
        self._focused_node_id = node_id
        
        # Return tabindex directive: focused node gets 0, others get -1
        return {
            'focused': node_id,
            'tabindex': '0'
        }
    
    def restore_previous_focus(self) -> Optional[str]:
        """!
        @brief Restore focus to the previous node.
        
        @return ID of the restored focused node, or None if no history
        """
        if not self._focus_history:
            return None
        
        # Pop from history and restore
        self._focused_node_id = self._focus_history.pop()
        return self._focused_node_id
    
    def get_focused_node_id(self) -> Optional[str]:
        """!
        @brief Get the currently focused node ID.
        
        @return ID of focused node, or None if no focus
        """
        return self._focused_node_id
    
    def clear_history(self) -> None:
        """!
        @brief Clear the focus history.
        """
        self._focus_history.clear()


# ============================================================================
# ARIA Navigator
# ============================================================================

class ARIANavigator(MathNavigator):
    """!
    @brief Enhanced navigator with ARIA support and mode switching.
    
    @details
    Extends MathNavigator to add:
    - Mode switching (Browse/Explore/Verbose Learning)
    - Screen reader announcements
    - ARIA attribute generation
    - Keyboard command mapping
    - Context-aware hints
    
    @section aria_nav_example Example Usage
    @code{.py}
    from accessible_math_reader.core.aria_navigator import ARIANavigator
    from accessible_math_reader.config import NavigationMode
    
    nav = ARIANavigator(semantic_tree, config)
    
    # Switch to verbose learning mode
    nav.switch_mode(NavigationMode.VERBOSE_LEARNING)
    
    # Get announcement for screen reader
    print(nav.get_announcement())
    # "You are at the fraction. This shows division. Numerator is a, denominator is b."
    
    # Get ARIA attributes for current node
    attrs = nav.get_aria_attributes()
    # {'id': 'math-node-abc123', 'role': 'group', 'aria-label': 'fraction', ...}
    
    # Navigate and get keyboard hints
    nav.enter()
    print(nav.get_keyboard_map())
    # Shows available navigation commands
    @endcode
    """
    
    def __init__(
        self,
        root: SemanticNode,
        config: Optional[Config] = None
    ) -> None:
        """!
        @brief Initialize ARIA navigator.
        
        @param root Root semantic node
        @param config Accessibility configuration (uses defaults if None)
        """
        # Initialize base navigator
        super().__init__(root)
        
        # Store config (or use default)
        from accessible_math_reader.config import Config
        self.config = config or Config()
        
        # Current navigation mode
        self._mode = self.config.accessibility.navigation_mode
        
        # Focus manager for roving tabindex
        self._focus_manager = FocusManager()
        
        # Set initial focus to root
        self._focus_manager.set_focus(root.node_id)
        
        # Announcement queue for ARIA live regions
        self._announcement_queue: list[str] = []
    
    @property
    def current_mode(self) -> NavigationMode:
        """!
        @brief Get the current navigation mode.
        
        @return Current NavigationMode
        """
        return self._mode
    
    def switch_mode(self, mode: NavigationMode) -> str:
        """!
        @brief Switch to a different navigation mode.
        
        @details
        Different modes provide different levels of detail:
        - BROWSE: High-level, jump between major terms
        - EXPLORE: Detailed interactive navigation
        - VERBOSE_LEARNING: Extended descriptions with hints
        
        @param mode New NavigationMode to switch to
        @return Announcement text for the mode switch
        """
        old_mode = self._mode
        self._mode = mode
        
        # Generate mode switch announcement
        mode_names = {
            NavigationMode.BROWSE: "Browse mode",
            NavigationMode.EXPLORE: "Explore mode",
            NavigationMode.VERBOSE_LEARNING: "Verbose learning mode"
        }
        
        announcement = f"Switched to {mode_names[mode]}. "
        
        # Add mode-specific help
        if mode == NavigationMode.BROWSE:
            announcement += "Use arrow keys to jump between major terms."
        elif mode == NavigationMode.EXPLORE:
            announcement += "Use Enter to drill down, Escape to go up, arrows to move between siblings."
        elif mode == NavigationMode.VERBOSE_LEARNING:
            announcement += "Extended descriptions will be provided with pedagogical hints."
        
        # Queue the announcement
        self._announcement_queue.append(announcement)
        
        return announcement
    
    def get_announcement(self) -> str:
        """!
        @brief Get the announcement text for current position.
        
        @details
        Generates appropriate announcement based on navigation mode
        and current node type. Used to populate ARIA live regions.
        
        @return Text to announce to screen readers
        """
        node = self.current
        
        # Use pre-computed spoken text if available
        if 'spoken_text' in node.accessibility_metadata:
            base_text = node.accessibility_metadata['spoken_text']
        else:
            # Generate from node type and content
            base_text = self._generate_description(node)
        
        # Enhance based on mode
        if self._mode == NavigationMode.BROWSE:
            # Brief overview
            return base_text
        
        elif self._mode == NavigationMode.EXPLORE:
            # Add navigation hint
            hint = node.accessibility_metadata.get('navigation_hint', '')
            if not hint:
                hint = self._generate_navigation_hint(node)
            return f"{base_text}. {hint}"
        
        elif self._mode == NavigationMode.VERBOSE_LEARNING:
            # Add detailed description and pedagogical hints
            description = node.accessibility_metadata.get('description', '')
            if not description:
                description = self._generate_verbose_description(node)
            return f"{base_text}. {description}"
        
        return base_text
    
    def _generate_description(self, node: SemanticNode) -> str:
        """!
        @brief Generate basic description for a node.
        
        @param node Node to describe
        @return Description text
        """
        node_type = node.node_type
        
        # Use aria_label if available
        if 'aria_label' in node.accessibility_metadata:
            return node.accessibility_metadata['aria_label']
        
        # Generate based on node type
        descriptions = {
            NodeType.ROOT: "mathematical expression",
            NodeType.NUMBER: f"number {node.content}",
            NodeType.IDENTIFIER: f"variable {node.content}",
            NodeType.FRACTION: "fraction",
            NodeType.SUPERSCRIPT: "superscript",
            NodeType.SUBSCRIPT: "subscript",
            NodeType.SQRT: "square root",
            NodeType.NROOT: "n-th root",
            NodeType.SUM: "summation",
            NodeType.INTEGRAL: "integral",
            NodeType.OPERATOR: f"operator {node.content}",
            NodeType.RELATION: f"relation {node.content}",
        }
        
        return descriptions.get(node_type, node_type.name.lower())
    
    def _generate_navigation_hint(self, node: SemanticNode) -> str:
        """!
        @brief Generate navigation hint for a node.
        
        @param node Node to generate hint for
        @return Navigation hint text
        """
        hints = []
        
        # Can we go deeper?
        if node.children:
            hints.append(\"Press Enter to explore\")
        
        # Can we go to siblings?
        if node.parent:
            siblings = node.parent.get_navigable_children()
            idx = siblings.index(node) if node in siblings else -1
            if idx > 0:
                hints.append(\"Left arrow for previous\")
            if idx < len(siblings) - 1:
                hints.append(\"Right arrow for next\")
        
        # Can we go up?
        if node.parent and node.parent.node_type != NodeType.ROOT:
            hints.append(\"Escape to go up\")
        
        return \". \".join(hints) if hints else \"No navigation available\"
    
    def _generate_verbose_description(self, node: SemanticNode) -> str:
        """!
        @brief Generate verbose pedagogical description.
        
        @param node Node to describe
        @return Verbose description with learning hints
        """
        node_type = node.node_type
        
        # Pedagogical descriptions for learning mode
        descriptions = {
            NodeType.FRACTION: (
                \"A fraction represents division. It has a numerator (top) \"
                \"and a denominator (bottom). The numerator is divided by the denominator.\"
            ),
            NodeType.SUPERSCRIPT: (
                \"A superscript represents exponentiation or power. \"
                \"The base is raised to the power of the exponent.\"
            ),
            NodeType.SQRT: (
                \"A square root asks: what number, when multiplied by itself, \"
                \"gives the number inside the root?\"
            ),
            NodeType.SUM: (
                \"A summation adds up a sequence of terms. \"
                \"The variable below shows what changes, and the limits show the range.\"
            ),
            NodeType.INTEGRAL: (
                \"An integral calculates the area under a curve or the accumulated change. \"
                \"It's the reverse operation of differentiation.\"
            ),
        }
        
        return descriptions.get(node_type, self._generate_description(node))
    
    def get_aria_attributes(self) -> dict[str, str]:
        """!
        @brief Get ARIA attributes for the current node.
        
        @details
        Returns ARIA attributes ready to be applied to HTML elements.
        Includes proper tabindex based on focus state.
        
        @return Dictionary of ARIA attributes
        """
        node = self.current
        attrs = node.get_aria_attributes()
        
        # Set tabindex based on focus state
        is_focused = self._focus_manager.get_focused_node_id() == node.node_id
        attrs['tabindex'] = '0' if is_focused else '-1'
        
        return attrs
    
    def get_keyboard_map(self) -> dict[str, str]:
        """!
        @brief Get available keyboard commands for current position.
        
        @return Dictionary mapping command descriptions to key bindings
        """
        node = self.current
        commands = {}
        
        # Navigation commands
        if node.children:
            commands[\"Explore this element\"] = \"Enter\"
        
        if node.parent:
            siblings = node.parent.get_navigable_children()
            idx = siblings.index(node) if node in siblings else -1
            
            if idx > 0:
                commands[\"Previous sibling\"] = \"Left Arrow\"
            if idx < len(siblings) - 1:
                commands[\"Next sibling\"] = \"Right Arrow\"
            
            if node.parent.node_type != NodeType.ROOT:
                commands[\"Go to parent\"] = \"Escape\"
        
        # Mode switching
        commands[\"Switch mode\"] = \"M\"
        
        # Context help
        if self.config.accessibility.enable_context_help:
            commands[\"Where am I?\"] = \"?\"
        
        # Help
        commands[\"Show all shortcuts\"] = \"H\"
        
        return commands
    
    def enter(self) -> bool:
        """!
        @brief Move into current node's children with focus update.
        
        @return True if successful, False otherwise
        """
        success = super().enter()
        
        if success:
            # Update focus
            self._focus_manager.set_focus(self.current.node_id)
            
            # Queue announcement
            announcement = self.get_announcement()
            self._announcement_queue.append(announcement)
        
        return success
    
    def exit(self) -> bool:
        """!
        @brief Move to parent node with focus update.
        
        @return True if successful, False otherwise
        """
        success = super().exit()
        
        if success:
            # Update focus
            self._focus_manager.set_focus(self.current.node_id)
            
            # Queue announcement
            announcement = self.get_announcement()
            self._announcement_queue.append(announcement)
        
        return success
    
    def next(self) -> bool:
        """!
        @brief Move to next sibling with focus update.
        
        @return True if successful, False otherwise
        """
        success = super().next()
        
        if success:
            # Update focus
            self._focus_manager.set_focus(self.current.node_id)
            
            # Queue announcement
            announcement = self.get_announcement()
            self._announcement_queue.append(announcement)
        
        return success
    
    def previous(self) -> bool:
        """!
        @brief Move to previous sibling with focus update.
        
        @return True if successful, False otherwise
        """
        success = super().previous()
        
        if success:
            # Update focus
            self._focus_manager.set_focus(self.current.node_id)
            
            # Queue announcement
            announcement = self.get_announcement()
            self._announcement_queue.append(announcement)
        
        return success
    
    def get_next_announcement(self) -> Optional[str]:
        """!
        @brief Get the next announcement from the queue.
        
        @details
        Used by the frontend to populate ARIA live regions.
        Removes the announcement from the queue.
        
        @return Next announcement text, or None if queue is empty
        """
        if self._announcement_queue:
            return self._announcement_queue.pop(0)
        return None
    
    def clear_announcements(self) -> None:
        """!
        @brief Clear all pending announcements.
        """
        self._announcement_queue.clear()
    
    def get_context(self) -> str:
        """!
        @brief Get \"Where am I?\" context information.
        
        @details
        Provides breadcrumb trail and position information.
        Useful for users who get lost in complex expressions.
        
        @return Context description with breadcrumb trail
        """
        if not self.config.accessibility.enable_context_help:
            return \"Context help is disabled\"
        
        # Get path from root to current
        path = self.get_path()
        
        # Build breadcrumb
        breadcrumb_parts = []
        for node in path:
            if node.node_type == NodeType.ROOT:
                breadcrumb_parts.append(\"Root\")
            elif 'aria_label' in node.accessibility_metadata:
                breadcrumb_parts.append(node.accessibility_metadata['aria_label'])
            else:
                breadcrumb_parts.append(self._generate_description(node))
        
        breadcrumb = \" → \".join(breadcrumb_parts)
        
        # Add current position info
        current_desc = self._generate_description(self.current)
        
        # Add navigation hints
        hints = self._generate_navigation_hint(self.current)
        
        return (
            f\"You are at: {breadcrumb}\\n\"
            f\"Current element: {current_desc}\\n\"
            f\"Available actions: {hints}\"
        )
