import logging

from raito.utils.loggers import ColoredFormatter, MuteLoggersFilter


def _record(name="raito.core", level=logging.INFO, msg="hello"):
    return logging.LogRecord(name, level, "path.py", 1, msg, None, None)


def test_mute_filter_keeps_unlisted_logger():
    assert MuteLoggersFilter("other").filter(_record(name="raito.core")) is True


def test_mute_filter_drops_listed_logger():
    assert MuteLoggersFilter("raito.core").filter(_record(name="raito.core")) is False


def test_mute_filter_with_multiple_names():
    flt = MuteLoggersFilter("a", "b")
    assert flt.filter(_record(name="a")) is False
    assert flt.filter(_record(name="b")) is False
    assert flt.filter(_record(name="c")) is True


def test_mute_filter_no_names_keeps_everything():
    assert MuteLoggersFilter().filter(_record()) is True


def test_colored_formatter_returns_string_with_message():
    out = ColoredFormatter().format(_record(msg="my message"))
    assert isinstance(out, str)
    assert "my message" in out


def test_colored_formatter_includes_level_tag():
    out = ColoredFormatter().format(_record(level=logging.ERROR, msg="oops"))
    # single-letter level tag, e.g. "E" for ERROR
    assert "E" in out
    assert "oops" in out


def test_colored_formatter_handles_all_levels():
    for level in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL):
        out = ColoredFormatter().format(_record(level=level, msg="text"))
        assert "text" in out
