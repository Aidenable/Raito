from sqlalchemy import and_, delete
from sqlalchemy.dialects.postgresql import insert

from raito.plugins.roles.data import Role

from .sqlalchemy import SQLAlchemyRoleProvider, roles_table

__all__ = ("PostgreSQLRoleProvider",)


class PostgreSQLRoleProvider(SQLAlchemyRoleProvider):
    """PostgreSQL-based role provider.

    Required packages :code:`sqlalchemy[asyncio]`, :code:`asyncpg` package installed (:code:`pip install raito[postgresql]`)
    """

    async def set_role(self, bot_id: int, user_id: int, role: Role) -> None:
        """Set the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :param role: The role to assign
        :type role: Role
        """
        async with self.session_factory() as session:
            query = insert(roles_table).values(
                bot_id=bot_id,
                user_id=user_id,
                role=role.value,
            )
            query = query.on_conflict_do_update(
                index_elements=["bot_id", "user_id"],
                set_={"role": role.value},
            )
            await session.execute(query)
            await session.commit()

    async def remove_role(self, bot_id: int, user_id: int) -> None:
        """Remove the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
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
