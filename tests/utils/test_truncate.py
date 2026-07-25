from raito.utils.helpers.truncate import truncate


def test_truncates_long_text():
    assert truncate("Hello, world!", 8) == "Hello..."


def test_short_text_is_unchanged():
    assert truncate("short", 20) == "short"


def test_text_equal_to_limit_is_unchanged():
    assert truncate("exactly10!", 10) == "exactly10!"


def test_custom_ellipsis():
    assert truncate("Hello, world!", 6, ellipsis="…") == "Hello…"


def test_small_limit_keeps_only_ellipsis_tail():
    # max_length - len(ellipsis) == 0 -> only the ellipsis remains
    assert truncate("abcdef", 3) == "..."


def test_limit_smaller_than_ellipsis():
    # negative slice bound: text[:-1] + "..."
    assert truncate("abcdef", 2) == "abcde..."
