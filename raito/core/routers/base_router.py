from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram import Router

__all__ = ("BaseRouter",)


class BaseRouter:
    """Base class providing router linking and unlinking functionality."""

    def __init__(self, router: Router | None) -> None:
        """Initialize the BaseRouter instance.

        :param router: Router instance to manage
        :type router: Router | None, optional
        """
        self._router = router

    @property
    def router(self) -> Router | None:
        """Get the managed router instance.

        :return: The managed router instance or None if not set
        :rtype: Router | None
        """
        return self._router

    def _unlink_from_parent(self) -> None:
        """Unlink router from its parent router."""
        if not self._router or not self._router.parent_router:
            return

        parent = self._router.parent_router
        parent.sub_routers = [r for r in parent.sub_routers if r.name != self._router.name]

    def _link_to_parent(self, parent: Router) -> None:
        """Link router to a parent router.

        :param parent: Parent router to link to
        :type parent: Router
        """
        if self._router and self._router not in parent.sub_routers:
            parent.sub_routers.append(self._router)
