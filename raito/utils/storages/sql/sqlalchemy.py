from datetime import datetime
from typing import Any

from aiogram.fsm.storage.base import BaseStorage, StorageKey
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

__all__ = ("SQLAlchemyStorage",)

metadata = MetaData()

storage_table = Table(
    "raito__fsm_storage",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("key", String(255), nullable=False, unique=True, index=True),
    Column("state", String(255), nullable=True),
    Column("data", JSON, nullable=False, default={}),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column(
        "updated_at",
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    ),
)


class SQLAlchemyStorage(BaseStorage):
    """SQLAlchemy storage for FSM."""

    def __init__(
        self,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        key_separator: str = ":",
    ) -> None:
        """Initialize SQLAlchemyStorage.

        :param engine: SQLAlchemy async engine
        :type engine: AsyncEngine
        :param session_factory: Optional session factory
        :type session_factory: async_sessionmaker[AsyncSession] | None
        :param key_separator: Separator for key parts
        :type key_separator: str
        """
        self.engine = engine
        self.session_factory = session_factory or async_sessionmaker(engine, expire_on_commit=False)
        self.key_separator = key_separator

    @classmethod
    async def from_url(
        cls,
        url: str,
        *,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 0,
        **kwargs: Any,  # noqa: ANN401
    ) -> "SQLAlchemyStorage":
        """Create storage from database URL.

        :param url: Database URL
        :type url: str
        :param echo: Enable SQL logging
        :type echo: bool
        :param pool_size: Connection pool size
        :type pool_size: int
        :param max_overflow: Max overflow connections
        :type max_overflow: int
        :return: Configured storage instance
        :rtype: BaseSQLAlchemyStorage
        """
        engine = create_async_engine(
            url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        storage = cls(engine, **kwargs)
        await storage.migrate()
        return storage

    def _build_key(self, key: StorageKey) -> str:
        """Build string key from StorageKey.

        :param key: Storage key
        :type key: StorageKey
        :return: String representation
        :rtype: str
        """
        parts = [str(key.bot_id), str(key.chat_id), str(key.user_id)]
        if key.thread_id:
            parts.append(str(key.thread_id))
        if key.business_connection_id:
            parts.append(str(key.business_connection_id))
        if key.destiny:
            parts.append(key.destiny)
        return self.key_separator.join(parts)

    async def get_state(self, key: StorageKey) -> Any | None:  # noqa: ANN401
        """Get key state.

        :param key: Storage key
        :type key: StorageKey
        :return: Current state
        :rtype: str | None
        """
        str_key = self._build_key(key)
        async with self.session_factory() as session:
            query = select(storage_table.c.state).where(storage_table.c.key == str_key)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        """Get current data for key.

        :param key: Storage key
        :type key: StorageKey
        :return: Current data
        :rtype: Dict[str, Any]
        """
        str_key = self._build_key(key)
        async with self.session_factory() as session:
            query = select(storage_table.c.data).where(storage_table.c.key == str_key)
            result = await session.execute(query)
            return result.scalar_one_or_none() or {}

    async def update_data(self, key: StorageKey, data: dict[str, Any]) -> dict[str, Any]:
        """Update data in the storage for key.

        :param key: Storage key
        :type key: StorageKey
        :param data: Data to update
        :type data: Dict[str, Any]
        :return: Updated data
        :rtype: Dict[str, Any]
        """
        current_data = await self.get_data(key)
        current_data.update(data)
        await self.set_data(key, current_data)
        return current_data

    async def close(self) -> None:
        """Close the storage."""
        await self.engine.dispose()

    async def migrate(self) -> None:
        """Create tables if not exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
