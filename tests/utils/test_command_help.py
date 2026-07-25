from aiogram import html
from aiogram.filters import CommandObject

from raito.utils.helpers.command_help import get_command_help


def test_help_without_params_or_description():
    co = CommandObject(prefix="/", command="ping", args=None)
    out = get_command_help(co, {})
    assert out.startswith(html.bold("/ping"))
    assert html.code("/ping") in out
    # signature and example both collapse to just the command
    assert out.count(html.code("/ping")) == 2
    # no description blockquote
    assert "blockquote" not in out


def test_help_includes_param_placeholders_in_signature():
    co = CommandObject(prefix=".rt ", command="ban", args=None)
    out = get_command_help(co, {"user": str, "days": int})
    assert html.code(".rt ban [user] [days]") in out


def test_help_uses_example_values_for_types():
    co = CommandObject(prefix=".rt ", command="cfg", args=None)
    out = get_command_help(
        co,
        {"flag": bool, "name": str, "count": int, "ratio": float},
    )
    assert html.code(".rt cfg yes word 10 3.14") in out


def test_help_renders_description_block():
    co = CommandObject(prefix="/", command="start", args=None)
    out = get_command_help(co, {}, description="Begin here")
    assert html.expandable_blockquote(html.italic("Begin here")) in out


def test_help_bolds_the_command():
    co = CommandObject(prefix="/", command="status", args=None)
    out = get_command_help(co, {})
    assert html.bold("/status") in out
