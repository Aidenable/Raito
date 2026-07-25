"""Local fixtures for the roles plugin test suite."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from aiogram.fsm.storage.memory import MemoryStorage

from raito.plugins.roles.manager import RoleManager
from raito.plugins.roles.providers.memory import MemoryRoleProvider

BOT_ID = 42


@pytest.fixture
def mem_provider() -> MemoryRoleProvider:
    return MemoryRoleProvider(MemoryStorage())


@pytest.fixture
def manager(mem_provider: MemoryRoleProvider) -> RoleManager:
    return RoleManager(mem_provider)


@pytest.fixture
def make_manager() -> Callable[..., RoleManager]:
    def _make(developers: list[int] | None = None) -> RoleManager:
        provider = MemoryRoleProvider(MemoryStorage())
        return RoleManager(provider, developers=developers)

    return _make
