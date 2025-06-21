from sqlalchemy import (
    BigInteger,
    Column,
    Index,
    Integer,
    MetaData,
    Table,
    and_,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from raito.plugins.roles.data import Role
from raito.plugins.roles.providers.protocol import IRoleProvider
from raito.utils.storages.sql.sqlalchemy import SQLAlchemyStorage

__all__ = ("SQLAlchemyRoleProvider",)

metadata = MetaData()

roles_table = Table(
    "raito__user_roles",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("bot_id", BigInteger, nullable=False),
    Column("user_id", BigInteger, nullable=False),
    Column("role", Integer, nullable=False),
    Index("idx_bot_user", "bot_id", "user_id", unique=True),
)


class SQLAlchemyRoleProvider(IRoleProvider):
    """Base SQLAlchemy role provider."""

    def __init__(
        self,
        storage: SQLAlchemyStorage,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        """Initialize SQLAlchemyRoleProvider.

        :param engine: SQLAlchemy async engine
        :type engine: AsyncEngine
        :param session_factory: Optional session factory, defaults to None
        :type session_factory: async_sessionmaker[AsyncSession] | None
        """
        self.storage = storage
        self.engine = self.storage.engine
        self.session_factory = session_factory or async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_role(self, bot_id: int, user_id: int) -> Role | None:
        """Get the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :return: The user's role or None if not found
        :rtype: Role | None
        """
        async with self.session_factory() as session:
            query = select(roles_table.c.role).where(
                and_(
                    roles_table.c.bot_id == bot_id,
                    roles_table.c.user_id == user_id,
                ),
            )
            result = await session.execute(query)
            role_value = result.scalar_one_or_none()
            if role_value is None:
                return None

            if isinstance(role_value, str):
                role_value = int(role_value)
            return Role(role_value)

    async def migrate(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def close(self) -> None:
        """Close the database connection."""
        await self.engine.dispose()
