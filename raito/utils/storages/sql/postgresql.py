from datetime import datetime, timezone
from typing import Any

from aiogram.filters.state import StateType
from aiogram.fsm.storage.base import StorageKey
from sqlalchemy import URL
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine

from .sqlalchemy import SQLAlchemyStorage, storage_table

__all__ = ("PostgreSQLStorage",)


class PostgreSQLStorage(SQLAlchemyStorage):
    """PostgreSQL storage for FSM.

    Required packages :code:`sqlalchemy[asyncio]`, :code:`asyncpg` package installed (:code:`pip install raito[postgresql]`)
    """

    def __init__(self, url: str | URL) -> None:
        """Initialize SQLite storage.

        :param url: PostgreSQL database URL
        :type url: str | URL
        """
        self.url = url
        engine = create_async_engine(url=self.url)
        super().__init__(engine=engine)

    async def set_state(self, key: StorageKey, state: StateType | None = None) -> None:
        """Set state for specified key.

        :param key: Storage key
        :type key: StorageKey
        :param state: New state
        :type state: StateType | None
        """
        built_key = self._build_key(key)
        async with self.session_factory() as session:
            query = insert(storage_table).values(
                key=built_key,
                state=state,
                data={},
            )
            query = query.on_conflict_do_update(
                index_elements=["key"],
                set_={"state": state, "updated_at": datetime.now(tz=timezone.utc)},
            )
            await session.execute(query)
            await session.commit()

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        """Write data (replace).

        :param key: Storage key
        :type key: StorageKey
        :param data: New data
        :type data: Dict[str, Any]
        """
        str_key = self._build_key(key)
        async with self.session_factory() as session:
            query = insert(storage_table).values(
                key=str_key,
                data=data,
            )
            query = query.on_conflict_do_update(
                index_elements=["key"],
                set_={"data": data, "updated_at": datetime.now(tz=timezone.utc)},
            )
            await session.execute(query)
            await session.commit()
