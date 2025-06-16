from collections import defaultdict
from typing import Any

TreeNode = dict[str, Any]


def _build_tree(paths: list[str]) -> TreeNode:
    def tree() -> defaultdict[str, Any]:
        return defaultdict(tree)

    root = tree()
    for path in paths:
        node = root
        for part in path.split("."):
            node = node[part]
    return root


def _render_ascii(node: TreeNode, *, _prefix: str = "") -> list[str]:
    lines = []
    items = sorted(node.items())
    last_index = len(items) - 1

    for i, (key, children) in enumerate(items):
        is_last = i == last_index
        branch = "└" if is_last else "├"
        suffix = "/" if children else " "
        lines.append(f"{_prefix}{branch} {key}{suffix}")

        if children:
            extension = "  " if is_last else "│ "
            lines.extend(_render_ascii(children, _prefix=_prefix + extension))
    return lines


def ascii_tree(paths: list[str]) -> str:
    tree = _build_tree(paths)
    return "\n".join(_render_ascii(tree))
