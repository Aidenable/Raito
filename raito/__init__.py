from types import SimpleNamespace

from raito.utils.configuration import Configuration

from .core.raito import Raito
from .plugins.roles import Role, roles

rt = SimpleNamespace(
    Raito=Raito,
    roles=roles,
    Role=Role,
    Configuration=Configuration,
)

__all__ = ("Raito", "rt")
