import logging

__all__ = (
    "core",
    "middlewares",
    "plugins",
    "roles",
)

core = logging.getLogger("raito.core")
middlewares = logging.getLogger("raito.middlewares")

plugins = logging.getLogger("raito.plugins")
roles = logging.getLogger("raito.plugins.roles")
