# ============================================================================
# tests/core/test_semantic.py — SemanticNode & MathNavigator unit tests
# ============================================================================
"""
Tests for accessible_math_reader.core.semantic

Covers:
  - SemanticNode creation, tree building, traversal
  - MathNavigator navigation (enter/exit/next/previous/reset)
  - Serialization (to_dict / from_dict round-trip)
  - Accessibility metadata
"""

import pytest

from accessible_math_reader.core.semantic import SemanticNode, NodeType, MathNavigator


# ══════════════════════════════════════════════════════════════════════════
# SemanticNode
# ══════════════════════════════════════════════════════════════════════════


class TestSemanticNode:
    """Basic node construction, tree ops, and properties."""

    def test_create_leaf(self):
        node = SemanticNode(NodeType.NUMBER, content="42")
        assert node.node_type == NodeType.NUMBER
        assert node.content == "42"
        assert node.is_leaf
        assert len(node) == 0

    def test_add_child_sets_parent(self):
        parent = SemanticNode(NodeType.ROOT)
        child = SemanticNode(NodeType.IDENTIFIER, content="x")
        parent.add_child(child)
        assert child.parent is parent
        assert len(parent) == 1

    def test_iteration(self):
        parent = SemanticNode(NodeType.ROOT)
        parent.add_child(SemanticNode(NodeType.NUMBER, content="1"))
        parent.add_child(SemanticNode(NodeType.NUMBER, content="2"))
        contents = [c.content for c in parent]
        assert contents == ["1", "2"]

    def test_getitem(self):
        parent = SemanticNode(NodeType.ROOT)
        child = SemanticNode(NodeType.NUMBER, content="7")
        parent.add_child(child)
        assert parent[0] is child

    def test_depth_root(self):
        node = SemanticNode(NodeType.ROOT)
        assert node.depth == 0

    def test_depth_child(self):
        root = SemanticNode(NodeType.ROOT)
        child = SemanticNode(NodeType.NUMBER, content="5")
        root.add_child(child)
        assert child.depth == 1

    def test_walk_preorder(self):
        root = SemanticNode(NodeType.ROOT)
        a = SemanticNode(NodeType.IDENTIFIER, content="a")
        b = SemanticNode(NodeType.IDENTIFIER, content="b")
        root.add_child(a)
        root.add_child(b)
        walked = list(root.walk())
        assert walked[0] is root
        assert walked[1] is a
        assert walked[2] is b

    def test_walk_leaves(self):
        root = SemanticNode(NodeType.ROOT)
        group = SemanticNode(NodeType.GROUP)
        leaf = SemanticNode(NodeType.NUMBER, content="3")
        group.add_child(leaf)
        root.add_child(group)
        leaves = list(root.walk_leaves())
        assert leaves == [leaf]

    def test_to_dict_and_from_dict_roundtrip(self):
        root = SemanticNode(NodeType.ROOT)
        root.add_child(SemanticNode(NodeType.NUMBER, content="42"))
        d = root.to_dict()

        restored = SemanticNode.from_dict(d)
        assert restored.node_type == NodeType.ROOT
        assert len(restored.children) == 1
        assert restored.children[0].content == "42"

    def test_node_id_unique(self):
        a = SemanticNode(NodeType.NUMBER, content="1")
        b = SemanticNode(NodeType.NUMBER, content="1")
        assert a.node_id != b.node_id

    def test_set_accessibility_metadata(self):
        node = SemanticNode(NodeType.FRACTION)
        node.set_accessibility_metadata(
            spoken_text="a over b",
            aria_role="math",
            aria_label="fraction a over b",
        )
        assert node.accessibility_metadata["spoken_text"] == "a over b"
        assert node.accessibility_metadata["aria_role"] == "math"

    def test_get_aria_attributes(self):
        node = SemanticNode(NodeType.FRACTION)
        node.set_accessibility_metadata(aria_role="group", aria_label="fraction")
        attrs = node.get_aria_attributes()
        assert attrs["role"] == "group"
        assert attrs["aria-label"] == "fraction"


# ══════════════════════════════════════════════════════════════════════════
# MathNavigator
# ══════════════════════════════════════════════════════════════════════════


class TestMathNavigator:
    """Test keyboard-style navigation through a math tree."""

    @pytest.fixture()
    def sample_tree(self):
        """Build: ROOT → FRACTION → [GROUP(a), GROUP(b)]"""
        root = SemanticNode(NodeType.ROOT)
        frac = SemanticNode(NodeType.FRACTION)
        num = SemanticNode(NodeType.IDENTIFIER, content="a")
        denom = SemanticNode(NodeType.IDENTIFIER, content="b")
        frac.add_child(num)
        frac.add_child(denom)
        root.add_child(frac)
        return root

    def test_starts_at_root(self, sample_tree):
        nav = MathNavigator(sample_tree)
        assert nav.current is sample_tree

    def test_enter(self, sample_tree):
        nav = MathNavigator(sample_tree)
        assert nav.enter()  # into fraction
        assert nav.current.node_type == NodeType.FRACTION

    def test_enter_twice(self, sample_tree):
        nav = MathNavigator(sample_tree)
        nav.enter()  # into fraction
        nav.enter()  # into numerator
        assert nav.current.content == "a"

    def test_next_sibling(self, sample_tree):
        nav = MathNavigator(sample_tree)
        nav.enter()
        nav.enter()  # at "a"
        assert nav.next()  # move to "b"
        assert nav.current.content == "b"

    def test_previous_sibling(self, sample_tree):
        nav = MathNavigator(sample_tree)
        nav.enter()
        nav.enter()
        nav.next()  # at "b"
        assert nav.previous()
        assert nav.current.content == "a"

    def test_exit(self, sample_tree):
        nav = MathNavigator(sample_tree)
        nav.enter()
        assert nav.exit()
        assert nav.current is sample_tree

    def test_exit_at_root_returns_false(self, sample_tree):
        nav = MathNavigator(sample_tree)
        assert not nav.exit()

    def test_enter_leaf_returns_false(self):
        leaf = SemanticNode(NodeType.NUMBER, content="1")
        root = SemanticNode(NodeType.ROOT)
        root.add_child(leaf)
        nav = MathNavigator(root)
        nav.enter()
        assert not nav.enter()  # leaf has no children

    def test_next_at_end_returns_false(self, sample_tree):
        nav = MathNavigator(sample_tree)
        nav.enter()
        nav.enter()
        nav.next()  # at "b" (last)
        assert not nav.next()

    def test_reset(self, sample_tree):
        nav = MathNavigator(sample_tree)
        nav.enter()
        nav.enter()
        nav.reset()
        assert nav.current is sample_tree

    def test_get_path(self, sample_tree):
        nav = MathNavigator(sample_tree)
        nav.enter()
        nav.enter()
        path = nav.get_path()
        assert path[0] is sample_tree
        assert path[-1].content == "a"
