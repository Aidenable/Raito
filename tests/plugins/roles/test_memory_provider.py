"""Tests for MemoryRoleProvider / BaseRoleProvider storage behaviour."""

from __future__ import annotations

from aiogram.fsm.storage.memory import MemoryStorage

from raito.plugins.roles.providers.memory import MemoryRoleProvider

from .conftest import BOT_ID


async def test_get_role_none_initially(mem_provider: MemoryRoleProvider):
    assert await mem_provider.get_role(BOT_ID, 111) is None


async def test_set_and_get_role(mem_provider: MemoryRoleProvider):
    await mem_provider.set_role(BOT_ID, 111, "owner")
    assert await mem_provider.get_role(BOT_ID, 111) == "owner"


async def test_set_role_overwrites(mem_provider: MemoryRoleProvider):
    await mem_provider.set_role(BOT_ID, 111, "owner")
    await mem_provider.set_role(BOT_ID, 111, "guest")
    assert await mem_provider.get_role(BOT_ID, 111) == "guest"


async def test_remove_role(mem_provider: MemoryRoleProvider):
    await mem_provider.set_role(BOT_ID, 111, "owner")
    await mem_provider.remove_role(BOT_ID, 111)
    assert await mem_provider.get_role(BOT_ID, 111) is None


async def test_remove_missing_role_is_noop(mem_provider: MemoryRoleProvider):
    # Should not raise even if the user has no role.
    await mem_provider.remove_role(BOT_ID, 999)
    assert await mem_provider.get_role(BOT_ID, 999) is None


async def test_get_users_returns_matching(mem_provider: MemoryRoleProvider):
    await mem_provider.set_role(BOT_ID, 1, "guest")
    await mem_provider.set_role(BOT_ID, 2, "guest")
    await mem_provider.set_role(BOT_ID, 3, "owner")

    users = await mem_provider.get_users(BOT_ID, "guest")
    assert sorted(users) == [1, 2]
    assert await mem_provider.get_users(BOT_ID, "owner") == [3]


async def test_get_users_empty(mem_provider: MemoryRoleProvider):
    assert await mem_provider.get_users(BOT_ID, "tester") == []


async def test_bots_are_isolated():
    provider = MemoryRoleProvider(MemoryStorage())
    await provider.set_role(42, 1, "owner")
    await provider.set_role(43, 1, "guest")

    assert await provider.get_role(42, 1) == "owner"
    assert await provider.get_role(43, 1) == "guest"
    assert await provider.get_users(42, "owner") == [1]
    assert await provider.get_users(43, "owner") == []


async def test_migrate_is_noop(mem_provider: MemoryRoleProvider):
    assert await mem_provider.migrate() is None
