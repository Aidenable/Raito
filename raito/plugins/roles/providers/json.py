from raito.utils.storages.json import JSONStorage

from .base import BaseRoleProvider
from .protocol import IRoleProvider

__all__ = ("JSONRoleProvider",)


class JSONRoleProvider(BaseRoleProvider, IRoleProvider):
    """JSON-based role provider for testing and development."""

    def __init__(self, storage: JSONStorage) -> None:
        """Initialize JSONRoleProvider."""
        super().__init__(storage=storage)
