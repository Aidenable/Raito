from typing import TYPE_CHECKING, Literal, overload

__all__ = (
    "get_postgresql_storage",
    "get_sqlite_storage",
)

if TYPE_CHECKING:
    from aiogram.fsm.storage.redis import RedisStorage

    from .postgresql import PostgreSQLStorage
    from .sqlite import SQLiteStorage


@overload
def get_sqlite_storage(*, throw: Literal[True] = True) -> type["SQLiteStorage"]: ...
@overload
def get_sqlite_storage(*, throw: Literal[False]) -> type["SQLiteStorage"] | None: ...
def get_sqlite_storage(*, throw: bool = True) -> type["SQLiteStorage"] | None:
    try:
        from .sqlite import SQLiteStorage
    except ImportError as exc:
        if not throw:
            return None

        msg = "SQLiteStorage requires :code:`aiosqlite` package. Install it using :code:`pip install raito[sqlite]`"
        raise ImportError(msg) from exc

    return SQLiteStorage


@overload
def get_postgresql_storage(*, throw: Literal[True] = True) -> type["PostgreSQLStorage"]: ...
@overload
def get_postgresql_storage(*, throw: Literal[False]) -> type["PostgreSQLStorage"] | None: ...
def get_postgresql_storage(*, throw: bool = True) -> type["PostgreSQLStorage"] | None:
    try:
        from .postgresql import PostgreSQLStorage
    except ImportError as exc:
        if not throw:
            return None

        msg = "PostgreSQLStorage requires :code:`asyncpg`, :code:`sqlalchemy` package. Install it using :code:`pip install raito[postgresql]`"
        raise ImportError(msg) from exc

    return PostgreSQLStorage


@overload
def get_redis_storage(*, throw: Literal[True] = True) -> type["RedisStorage"]: ...
@overload
def get_redis_storage(*, throw: Literal[False]) -> type["RedisStorage"] | None: ...
def get_redis_storage(*, throw: bool = True) -> type["RedisStorage"] | None:
    try:
        from aiogram.fsm.storage.redis import RedisStorage
    except ImportError as exc:
        if not throw:
            return None

        msg = "RedisStorage requires :code:`redis` package. Install it using :code:`pip install raito[redis]`"
        raise ImportError(msg) from exc

    return RedisStorage
