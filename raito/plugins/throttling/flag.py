from __future__ import annotations

from aiogram.dispatcher.flags import Flag, FlagDecorator

from .middleware import THROTTLING_MODE

__all__ = ("limiter",)


def limiter(rate_limit: float, mode: THROTTLING_MODE = "user") -> FlagDecorator:
    """Attach a rate limit to the command handler.

    This decorator sets a custom rate limit (in seconds) for a specific command handler.

    :param rate_limit: Minimum delay between invokes (in seconds)
    :param mode: Throttling key type: 'user', 'chat', or 'bot'
    :return: Combined FlagDecorator
    """
    data = {"rate_limit": rate_limit, "mode": mode}
    return FlagDecorator(Flag("raito__limiter", value=data))
