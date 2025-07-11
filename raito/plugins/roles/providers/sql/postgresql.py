from sqlalchemy import and_, delete
from sqlalchemy.dialects.postgresql import insert

from .sqlalchemy import SQLAlchemyRoleProvider, roles_table

__all__ = ("PostgreSQLRoleProvider",)


class PostgreSQLRoleProvider(SQLAlchemyRoleProvider):
    """PostgreSQL-based role provider.

    Required packages :code:`sqlalchemy[asyncio]`, :code:`asyncpg` package installed (:code:`pip install raito[postgresql]`)
    """

    async def set_role(self, bot_id: int, user_id: int, role_slug: str) -> None:
        """Set the role for a specific user.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :param role_slug: The role slug to assign
        """
        async with self.session_factory() as session:
            query = insert(roles_table).values(
                bot_id=bot_id,
                user_id=user_id,
                role=role_slug,
            )
            query = query.on_conflict_do_update(
                index_elements=["bot_id", "user_id"],
                set_={"role": role_slug},
            )
            await session.execute(query)
            await session.commit()

    async def remove_role(self, bot_id: int, user_id: int) -> None:
        """Remove the role for a specific user.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        """
        async with self.session_factory() as session:
            query = delete(roles_table).where(
                and_(
                    roles_table.c.bot_id == bot_id,
                    roles_table.c.user_id == user_id,
                ),
            )
            await session.execute(query)
            await session.commit()
