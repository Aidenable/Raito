from contextlib import suppress

from .memory import MemoryRoleProvider
from .protocol import IRoleProvider

RedisRoleProvider = None
SQLiteRoleProvider = None
PostgreSQLRoleProvider = None

with suppress(ImportError):
    from .redis import RedisRoleProvider

with suppress(ImportError):
    from .sql.postgresql import PostgreSQLRoleProvider

with suppress(ImportError):
    from .sql.sqlite import SQLiteRoleProvider

__all__ = [
    "IRoleProvider",
    "MemoryRoleProvider",
]

if RedisRoleProvider is not None:
    __all__ += ["RedisRoleProvider"]

if PostgreSQLRoleProvider is not None:
    __all__ += ["PostgreSQLRoleProvider"]

if SQLiteRoleProvider is not None:
    __all__ += ["SQLiteRoleProvider"]
