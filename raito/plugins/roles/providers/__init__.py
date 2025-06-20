from typing import TYPE_CHECKING, overload

from .base import BaseRoleProvider
from .memory import MemoryRoleProvider
from .protocol import IRoleProvider
from .sql import get_postgresql_provider, get_sqlite_provider

if TYPE_CHECKING:
    from .redis import RedisRoleProvider

__all__ = (
    "BaseRoleProvider",
    "IRoleProvider",
    "MemoryRoleProvider",
    "get_postgresql_provider",
    "get_redis_provider",
    "get_sqlite_provider",
)


@overload
def get_redis_provider() -> type["RedisRoleProvider"]: ...
@overload
def get_redis_provider(*, throw: bool = False) -> type["RedisRoleProvider"] | None: ...
def get_redis_provider(*, throw: bool = True) -> type["RedisRoleProvider"] | None:
    try:
        from .redis import RedisRoleProvider
    except ImportError as exc:
        if not throw:
            return None

        msg = (
            "RedisRoleProvider requires redis package. Install it using `pip install raito[redis]`"
        )
        raise ImportError(msg) from exc

    return RedisRoleProvider
