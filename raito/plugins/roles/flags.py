from aiogram.dispatcher.flags import Flag, FlagDecorator

from .data import Role

__all__ = ("roles",)


def roles(*allowed_roles: Role) -> FlagDecorator:
    return FlagDecorator(Flag("raito__roles", value=True))(allowed_roles)
