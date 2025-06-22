from collections.abc import Callable
from typing import NamedTuple, Optional

from pydantic import BaseModel

__all__ = (
    "NodeParts",
    "TreeChars",
    "TreeNode",
    "dot_paths_to_tree",
)


class TreeChars(BaseModel):
    """Tree branch characters for ASCII tree rendering."""

    last: str = "╚"
    middle: str = "╠"
    vertical: str = "║"


class NodeParts(NamedTuple):
    """Parts of a tree node."""

    icon: str
    folder: str
    prefix: str
    suffix: str


class TreeNode:
    """Tree node with support for prefixes, suffixes and customizable display."""

    def __init__(
        self,
        name: str,
        prefix: str = "",
        suffix: str = "",
        *,
        is_folder: bool = False,
    ) -> None:
        """Initialize TreeNode.

        :param name: Node name
        :type name: str
        :param prefix: Node prefix
        :type prefix: str
        :param suffix: Node suffix
        :type suffix: str
        :param is_folder: Whether the node represents a folder
        :type is_folder: bool
        """
        self.name = name
        self.prefix = prefix
        self.suffix = suffix
        self.is_folder = is_folder
        self.children: dict[str, TreeNode] = {}

    def add_child(
        self,
        name: str,
        prefix: str = "",
        suffix: str = "",
        *,
        is_folder: bool = False,
    ) -> "TreeNode":
        """Add a child node to this node.

        :param name: Child node name
        :type name: str
        :param prefix: Child node prefix
        :type prefix: str
        :param suffix: Child node suffix
        :type suffix: str
        :param is_folder: Whether the child node is a folder
        :type is_folder: bool
        :returns: The child node (new or existing)
        :rtype: TreeNode
        """
        if name not in self.children:
            self.children[name] = TreeNode(name, prefix, suffix, is_folder=is_folder)
        else:
            if prefix:
                self.children[name].prefix = prefix
            if suffix:
                self.children[name].suffix = suffix
            if is_folder:
                self.children[name].is_folder = True
        return self.children[name]

    def get_child(self, name: str) -> Optional["TreeNode"]:
        """Get a child node by name.

        :param name: Child node name
        :type name: str
        :returns: Child node if found, None otherwise
        :rtype: TreeNode | None
        """
        return self.children.get(name)

    def __repr__(self) -> str:
        """Return a string representation of the TreeNode.

        :returns: String representation of the TreeNode
        :rtype: str
        """
        return f"<TreeNode {self.name=} {self.prefix=} {self.suffix=} {self.is_folder=}>"


class AsciiTree:
    """ASCII tree renderer with customizable styling."""

    def __init__(
        self,
        folder_icon: str = "📁",
        folder_suffix: str = "/",
        tree_chars: TreeChars | None = None,
    ) -> None:
        """Initialize AsciiTree.

        :param folder_icon: Icon for folder nodes
        :type folder_icon: str
        :param folder_suffix: Suffix for folder nodes (e.g., "/")
        :type folder_suffix: str
        :param tree_chars: Tree characters (last, middle, vertical)
        :type tree_chars: TreeChars
        """
        self.folder_icon = folder_icon
        self.folder_suffix = folder_suffix
        self.tree_chars = tree_chars or TreeChars()

    def render(self, root: TreeNode) -> str:
        """Render the tree to ASCII format.

        :param root: Root node of the tree
        :type root: TreeNode
        :returns: ASCII rendered tree
        :rtype: str
        """
        if not root.children:
            return ""

        lines: list[str] = []
        self._render_children(root.children, "", lines)
        return "\n".join(lines)

    def _render_children(
        self,
        children: dict[str, TreeNode],
        prefix: str,
        lines: list[str],
    ) -> None:
        """Render child nodes recursively.

        :param children: Dictionary of child nodes
        :type children: dict[str, TreeNode]
        :param prefix: Current line prefix for indentation
        :type prefix: str
        :param lines: List to accumulate rendered lines
        :type lines: list[str]
        """
        sorted_children = sorted(children.items())
        last_index = len(sorted_children) - 1

        for i, (_, node) in enumerate(sorted_children):
            is_last = i == last_index
            branch = self.tree_chars.last if is_last else self.tree_chars.middle

            parts = NodeParts(
                icon=f"{self.folder_icon} " if node.is_folder and self.folder_icon else "",
                folder=self.folder_suffix if node.is_folder else "",
                prefix=f"{node.prefix} " if node.prefix and not node.is_folder else "",
                suffix=f" {node.suffix}" if node.suffix and not node.is_folder else "",
            )

            line = f"{prefix}{branch} {parts.prefix}{parts.icon}{node.name}{parts.folder}{parts.suffix}"
            lines.append(line)

            if node.children:
                empty = " " * 4
                extension = empty if is_last else f"{self.tree_chars.vertical}" + empty[1:]
                self._render_children(node.children, prefix + extension, lines)


def dot_paths_to_tree(
    paths: list[str] | dict[str, str],
    prefix_callback: Callable[[str], str | None] | None = None,
    suffix_callback: Callable[[str], str | None] | None = None,
) -> TreeNode:
    """Convert dot-notation paths to a tree structure.

    :param paths: List of paths ["folder.child", "folder.folder.child"]
    :type paths: list[str]
    :param prefix_callback: Function to get node prefixes
    :type prefix_callback: Callable[[str], str | None] | None
    :param suffix_callback: Function to get node suffixes
    :type suffix_callback: Callable[[str], str | None] | None
    :returns: Root node of the tree
    :rtype: TreeNode
    """
    root = TreeNode("root", is_folder=True)

    for path in paths:
        parts = path.split(".")
        current_node = root

        for i, part in enumerate(parts):
            is_last_part = i == len(parts) - 1
            current_path = ".".join(parts[: i + 1])

            prefix, suffix = "", ""
            if prefix_callback:
                prefix = prefix_callback(current_path) or ""
            if suffix_callback:
                suffix = suffix_callback(current_path) or ""

            is_folder = not is_last_part or any(
                other_path.startswith(current_path + ".")
                for other_path in paths
                if other_path != current_path
            )

            current_node = current_node.add_child(part, prefix, suffix, is_folder=is_folder)

    return root
