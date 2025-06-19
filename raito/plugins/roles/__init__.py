from contextlib import suppress

from .data import ROLES_DATA, Role
from .flags import roles
from .manager import RoleManager
from .providers import IRoleProvider, MemoryRoleProvider

RedisRoleProvider = None
PostgreSQLRoleProvider = None
SQLiteRoleProvider = None

with suppress(ImportError):
    from .providers import RedisRoleProvider

with suppress(ImportError):
    from .providers import PostgreSQLRoleProvider

with suppress(ImportError):
    from .providers import SQLiteRoleProvider

__all__ = [
    "ROLES_DATA",
    "IRoleProvider",
    "MemoryRoleProvider",
    "Role",
    "RoleManager",
    "roles",
]

if RedisRoleProvider is not None:
    __all__ += ["RedisRoleProvider"]

if PostgreSQLRoleProvider is not None:
    __all__ += ["PostgreSQLRoleProvider"]

if SQLiteRoleProvider is not None:
    __all__ += ["SQLiteRoleProvider"]
