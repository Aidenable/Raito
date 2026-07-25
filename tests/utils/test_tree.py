from raito.utils.ascii.tree import AsciiTree, TreeNode, dot_paths_to_tree


def test_add_child_returns_new_node():
    root = TreeNode("root")
    child = root.add_child("a")
    assert isinstance(child, TreeNode)
    assert child.name == "a"
    assert root.get_child("a") is child


def test_add_child_is_idempotent_and_updates_attrs():
    root = TreeNode("root")
    first = root.add_child("a")
    second = root.add_child("a", prefix="P", suffix="S", is_folder=True)
    assert first is second
    assert len(root.children) == 1
    assert second.prefix == "P"
    assert second.suffix == "S"
    assert second.is_folder is True


def test_render_empty_root_is_blank():
    assert AsciiTree().render(TreeNode("root")) == ""


def test_render_single_child_uses_last_branch():
    root = TreeNode("root")
    root.add_child("only")
    assert AsciiTree().render(root) == "╚ only"


def test_render_sorts_and_uses_middle_and_last():
    root = TreeNode("root")
    root.add_child("b")
    root.add_child("a")
    rendered = AsciiTree().render(root)
    assert rendered == "╠ a\n╚ b"


def test_render_prefix_and_suffix_on_leaf():
    root = TreeNode("root")
    root.add_child("file", prefix="+", suffix="!")
    assert AsciiTree().render(root) == "╚ + file !"


def test_render_folder_icon_and_suffix():
    root = TreeNode("root")
    root.add_child("dir", is_folder=True)
    assert AsciiTree().render(root) == "╚ 📁 dir/"


def test_render_nested_structure_indentation():
    root = dot_paths_to_tree(["a.b.c", "a.b.d", "x"])
    expected = "\n".join(
        [
            "╠ 📁 a/",
            "║   ╚ 📁 b/",
            "║       ╠ c",
            "║       ╚ d",
            "╚ x",
        ]
    )
    assert AsciiTree().render(root) == expected


def test_dot_paths_marks_folders_and_leaves():
    root = dot_paths_to_tree(["a.b", "a.c"])
    node_a = root.get_child("a")
    assert node_a is not None
    assert node_a.is_folder is True
    assert node_a.get_child("b").is_folder is False
    assert node_a.get_child("c").is_folder is False


def test_dot_paths_callbacks():
    def prefix_cb(path):
        return "P" if path == "a" else None

    def suffix_cb(path):
        return "S" if path == "a.b" else None

    root = dot_paths_to_tree(["a.b"], prefix_callback=prefix_cb, suffix_callback=suffix_cb)
    node_a = root.get_child("a")
    assert node_a.prefix == "P"
    assert node_a.get_child("b").suffix == "S"
