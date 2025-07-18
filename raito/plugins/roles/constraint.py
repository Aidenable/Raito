from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram.filters import Filter, or_f

if TYPE_CHECKING:
    from .filter import RoleFilter

__all__ = (
    "RoleConstraint",
    "RoleGroupConstraint",
)


class RoleConstraint(Filter):
    """Wrapper around RoleFilter that supports logical OR composition."""

    def __init__(self, filter: RoleFilter) -> None:
        """Initialize RoleConstraint.

        :param filter: An instance of RoleFilter
        """
        self.filter = filter

    def __or__(self, other: RoleConstraint | RoleGroupConstraint) -> RoleGroupConstraint:
        """Combine this marker with another using the `|` operator.

        :param other: Another RoleConstraint or RoleGroupConstraint
        :return: A combined RoleGroupConstraint
        """
        if isinstance(other, RoleGroupConstraint):
            return RoleGroupConstraint(self, *other.filters)
        return RoleGroupConstraint(self, other)

    __ror__ = __or__

    async def __call__(self, *args: Any, **kwargs: Any) -> bool:  # noqa: ANN401
        """Delegate the call to the inner filter."""
        return await self.filter(*args, **kwargs)


class RoleGroupConstraint(Filter):
    """Logical group of multiple RoleConstraints combined via OR."""

    def __init__(self, *filters: RoleConstraint) -> None:
        """Initialize RoleGroupConstraint.

        :param filters: One or more RoleConstraint instances
        """
        self.filters = filters

    def __or__(self, other: RoleConstraint | RoleGroupConstraint) -> RoleGroupConstraint:
        """Extend the group with another marker or group.

        :param other: Another RoleConstraint or RoleGroupConstraint
        :return: New RoleGroupConstraint with all combined filters
        """
        if isinstance(other, RoleGroupConstraint):
            return RoleGroupConstraint(*self.filters, *other.filters)
        return RoleGroupConstraint(*self.filters, other)

    async def __call__(self, *args: Any, **kwargs: Any) -> bool:  # noqa: ANN401
        """Convert the group into an `_OrFilter` filter."""
        or_filter = or_f(*[f.filter for f in self.filters])
        value = await or_filter(*args, **kwargs)
        return bool(value)
