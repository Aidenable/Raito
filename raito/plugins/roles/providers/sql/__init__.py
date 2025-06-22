from typing import TYPE_CHECKING, Literal, overload

__all__ = (
    "get_postgresql_provider",
    "get_sqlite_provider",
)

if TYPE_CHECKING:
    from .postgresql import PostgreSQLRoleProvider
    from .sqlite import SQLiteRoleProvider


@overload
def get_sqlite_provider(*, throw: Literal[True] = True) -> type["SQLiteRoleProvider"]: ...
@overload
def get_sqlite_provider(*, throw: Literal[False]) -> type["SQLiteRoleProvider"] | None: ...
def get_sqlite_provider(*, throw: bool = True) -> type["SQLiteRoleProvider"] | None:
    try:
        from .sqlite import SQLiteRoleProvider
    except ImportError as exc:
        if not throw:
            return None

        msg = "SQLiteRoleProvider requires :code:`aiosqlite` package. Install it using :code:`pip install raito[sqlite]`"
        raise ImportError(msg) from exc

    return SQLiteRoleProvider


@overload
def get_postgresql_provider(*, throw: Literal[True] = True) -> type["PostgreSQLRoleProvider"]: ...
@overload
def get_postgresql_provider(*, throw: Literal[False]) -> type["PostgreSQLRoleProvider"] | None: ...
def get_postgresql_provider(*, throw: bool = True) -> type["PostgreSQLRoleProvider"] | None:
    try:
        from .postgresql import PostgreSQLRoleProvider
    except ImportError as exc:
        if not throw:
            return None

        msg = "PostgreSQLRoleProvider requires :code:`asyncpg`, :code:`sqlalchemy` package. Install it using :code:`pip install raito[postgresql]`"
        raise ImportError(msg) from exc

    return PostgreSQLRoleProvider
