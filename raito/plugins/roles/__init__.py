from .data import ROLES_DATA, Role
from .flags import roles
from .manager import RoleManager
from .providers import IRoleProvider, MemoryRoleProvider

try:
    from .providers import RedisRoleProvider
except ImportError:
    RedisRoleProvider = None

__all__ = [
    "ROLES_DATA",
    "IRoleProvider",
    "MemoryRoleProvider",
    "Role",
    "RoleManager",
    "roles",
]

if RedisRoleProvider is not None:
    __all__ += ["RedisRoleProvider"]
