from sqlalchemy import (
    BigInteger,
    Column,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    and_,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

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
    Column("role", String, nullable=False),
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
        :param session_factory: Optional session factory, defaults to None
        """
        self.storage = storage
        self.engine = self.storage.engine
        self.session_factory = session_factory or async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_role(self, bot_id: int, user_id: int) -> str | None:
        """Get the role for a specific user.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :return: The role slug or None if not found
        """
        async with self.session_factory() as session:
            query = select(roles_table.c.role).where(
                and_(
                    roles_table.c.bot_id == bot_id,
                    roles_table.c.user_id == user_id,
                ),
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def migrate(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def close(self) -> None:
        """Close the database connection."""
        await self.engine.dispose()

    async def get_users(self, bot_id: int, role_slug: str) -> list[int]:
        """Get all users with a specific role.

        :param bot_id: The Telegram bot ID
        :param role_slug: The role slug to check for
        :return: A list of Telegram user IDs
        """
        async with self.session_factory() as session:
            query = select(roles_table.c.user_id).where(
                and_(
                    roles_table.c.bot_id == bot_id,
                    roles_table.c.role == role_slug,
                )
            )
            result = await session.execute(query)
            return [row[0] for row in result.all()]
