from aiogram.dispatcher.flags import Flag, FlagDecorator

from .data import Role


def roles(*allowed_roles: Role) -> FlagDecorator:
    return FlagDecorator(Flag("raito_roles", value=True))(allowed_roles)
