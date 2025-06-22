from aiogram.fsm.storage.redis import RedisStorage

from .base import BaseRoleProvider
from .protocol import IRoleProvider

__all__ = ("RedisRoleProvider",)


class RedisRoleProvider(BaseRoleProvider, IRoleProvider):
    """Redis-based role provider for testing and development.

    Redis storage required :code:`redis` package installed (:code:`pip install raito[redis]`)
    """

    def __init__(self, storage: RedisStorage) -> None:
        """Initialize RedisRoleProvider."""
        super().__init__(storage=storage)

        self.storage: RedisStorage
        self.storage.key_builder = self.key_builder
