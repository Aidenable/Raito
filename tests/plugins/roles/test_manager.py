"""Tests for RoleManager access-control logic."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from raito.plugins.roles.manager import RoleManager
from raito.plugins.roles.providers.memory import MemoryRoleProvider

from .conftest import BOT_ID

MANAGER_ROLES = ["developer", "administrator", "owner"]
NON_MANAGER_ROLES = ["moderator", "manager", "sponsor", "guest", "support", "tester"]


# --- assign_role -----------------------------------------------------------


async def test_assign_role_by_non_manager_raises(manager: RoleManager):
    with pytest.raises(PermissionError):
        await manager.assign_role(BOT_ID, initiator_id=100, target_id=200, role_slug="guest")
    # Nothing was persisted.
    assert await manager.get_role(BOT_ID, 200) is None


async def test_assign_role_by_user_without_role_raises(manager: RoleManager):
    await manager.provider.set_role(BOT_ID, 100, "moderator")
    with pytest.raises(PermissionError):
        await manager.assign_role(BOT_ID, initiator_id=100, target_id=200, role_slug="guest")


async def test_cannot_assign_own_role(manager: RoleManager):
    # Even an owner may not change their own role.
    await manager.provider.set_role(BOT_ID, 100, "owner")
    with pytest.raises(PermissionError):
        await manager.assign_role(BOT_ID, initiator_id=100, target_id=100, role_slug="guest")


@pytest.mark.parametrize("initiator_role", MANAGER_ROLES)
async def test_manager_roles_can_assign(manager: RoleManager, initiator_role: str):
    await manager.provider.set_role(BOT_ID, 100, initiator_role)
    await manager.assign_role(BOT_ID, initiator_id=100, target_id=200, role_slug="guest")
    assert await manager.get_role(BOT_ID, 200) == "guest"


async def test_developer_from_list_can_assign(make_manager: Callable[..., RoleManager]):
    manager = make_manager(developers=[100])
    await manager.assign_role(BOT_ID, initiator_id=100, target_id=200, role_slug="tester")
    assert await manager.get_role(BOT_ID, 200) == "tester"


# --- revoke_role -----------------------------------------------------------


async def test_revoke_role_by_owner(manager: RoleManager):
    await manager.provider.set_role(BOT_ID, 100, "owner")
    await manager.provider.set_role(BOT_ID, 200, "guest")

    await manager.revoke_role(BOT_ID, initiator_id=100, target_id=200)
    assert await manager.get_role(BOT_ID, 200) is None


async def test_revoke_role_by_non_manager_raises(manager: RoleManager):
    await manager.provider.set_role(BOT_ID, 200, "guest")
    with pytest.raises(PermissionError):
        await manager.revoke_role(BOT_ID, initiator_id=100, target_id=200)
    # Role stays intact.
    assert await manager.get_role(BOT_ID, 200) == "guest"


async def test_cannot_revoke_own_role(manager: RoleManager):
    await manager.provider.set_role(BOT_ID, 100, "owner")
    with pytest.raises(PermissionError):
        await manager.revoke_role(BOT_ID, initiator_id=100, target_id=100)


# --- has_role / has_any_roles ---------------------------------------------


async def test_has_role_true_and_false(manager: RoleManager):
    await manager.provider.set_role(BOT_ID, 5, "moderator")
    assert await manager.has_role(BOT_ID, 5, "moderator") is True
    assert await manager.has_role(BOT_ID, 5, "owner") is False
    assert await manager.has_role(BOT_ID, 6, "moderator") is False


async def test_has_role_developer_from_list(make_manager: Callable[..., RoleManager]):
    manager = make_manager(developers=[7])
    # Recognised as developer without any stored role.
    assert await manager.has_role(BOT_ID, 7, "developer") is True
    # The list only grants the "developer" role, nothing else.
    assert await manager.has_role(BOT_ID, 7, "owner") is False


async def test_has_any_roles(manager: RoleManager):
    await manager.provider.set_role(BOT_ID, 5, "administrator")
    assert await manager.has_any_roles(BOT_ID, 5, "owner", "administrator") is True
    assert await manager.has_any_roles(BOT_ID, 5, "owner", "moderator") is False
    assert await manager.has_any_roles(BOT_ID, 6, "owner") is False


async def test_has_any_roles_developer_from_list(make_manager: Callable[..., RoleManager]):
    manager = make_manager(developers=[7])
    # "developer" is among the requested roles -> short-circuits to True.
    assert await manager.has_any_roles(BOT_ID, 7, "developer", "owner") is True
    # "developer" not requested and no stored role -> False.
    assert await manager.has_any_roles(BOT_ID, 7, "owner", "administrator") is False


# --- can_manage_roles ------------------------------------------------------


@pytest.mark.parametrize("role", MANAGER_ROLES)
async def test_can_manage_roles_true(manager: RoleManager, role: str):
    await manager.provider.set_role(BOT_ID, 5, role)
    assert await manager.can_manage_roles(BOT_ID, 5) is True


@pytest.mark.parametrize("role", NON_MANAGER_ROLES)
async def test_can_manage_roles_false(manager: RoleManager, role: str):
    await manager.provider.set_role(BOT_ID, 5, role)
    assert await manager.can_manage_roles(BOT_ID, 5) is False


async def test_can_manage_roles_none_role(manager: RoleManager):
    assert await manager.can_manage_roles(BOT_ID, 5) is False


async def test_can_manage_roles_developer_from_list(make_manager: Callable[..., RoleManager]):
    manager = make_manager(developers=[7])
    assert await manager.can_manage_roles(BOT_ID, 7) is True


# --- get_users -------------------------------------------------------------


async def test_get_users_dedup(manager: RoleManager):
    await manager.provider.set_role(BOT_ID, 1, "guest")
    await manager.provider.set_role(BOT_ID, 2, "guest")
    users = await manager.get_users(BOT_ID, "guest")
    assert isinstance(users, set)
    assert users == {1, 2}


async def test_get_users_adds_developers_for_developer_role(
    make_manager: Callable[..., RoleManager],
):
    manager = make_manager(developers=[5, 6])
    await manager.provider.set_role(BOT_ID, 7, "developer")
    # Developer from the provider gets merged with the developers list, deduped.
    await manager.provider.set_role(BOT_ID, 5, "developer")

    users = await manager.get_users(BOT_ID, "developer")
    assert users == {5, 6, 7}


async def test_get_users_developers_not_added_for_other_roles(
    make_manager: Callable[..., RoleManager],
):
    manager = make_manager(developers=[5, 6])
    await manager.provider.set_role(BOT_ID, 1, "guest")
    assert await manager.get_users(BOT_ID, "guest") == {1}


# --- get_role_data / available_roles --------------------------------------


async def test_get_role_data(manager: RoleManager):
    data = manager.get_role_data("owner")
    assert data.slug == "owner"


async def test_available_roles_property(manager: RoleManager):
    slugs = {role.slug for role in manager.available_roles}
    assert "developer" in slugs
    assert len(manager.available_roles) == 9


def test_manager_defaults_developers_to_empty_list():
    from aiogram.fsm.storage.memory import MemoryStorage

    manager = RoleManager(MemoryRoleProvider(MemoryStorage()))
    assert manager.developers == []
