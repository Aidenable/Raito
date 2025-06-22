from aiogram.fsm.storage.memory import MemoryStorage

from .base import BaseRoleProvider
from .protocol import IRoleProvider

__all__ = ("MemoryRoleProvider",)


class MemoryRoleProvider(BaseRoleProvider, IRoleProvider):
    """Simple in-memory role provider for testing and development."""

    def __init__(self, storage: MemoryStorage) -> None:
        """Initialize MemoryRoleProvider."""
        super().__init__(storage=storage)
