from .memory import MemoryRoleProvider
from .protocol import IRoleProvider

try:
    from .redis import RedisRoleProvider
except ImportError:
    RedisRoleProvider = None

__all__ = [
    "IRoleProvider",
    "MemoryRoleProvider",
    "RedisRoleProvider",
]

if RedisRoleProvider is not None:
    __all__ += ["RedisRoleProvider"]
