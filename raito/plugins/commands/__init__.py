from .flags import description, hidden, params
from .middleware import CommandMiddleware
from .registration import register_bot_commands

__all__ = (
    "CommandMiddleware",
    "description",
    "hidden",
    "params",
    "register_bot_commands",
)
