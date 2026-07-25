"""Tests for RoleConstraint / RoleGroupConstraint composition and calling."""

from __future__ import annotations

from raito.rt import ADMINISTRATOR, DEVELOPER, GUEST, MODERATOR, OWNER
from raito.plugins.roles.constraint import RoleConstraint, RoleGroupConstraint

from .conftest import BOT_ID


# --- composition -----------------------------------------------------------


def test_constraint_or_constraint_builds_group():
    group = OWNER | ADMINISTRATOR
    assert isinstance(group, RoleGroupConstraint)
    assert group.filters == (OWNER, ADMINISTRATOR)


def test_group_or_constraint_extends():
    group = (OWNER | ADMINISTRATOR) | DEVELOPER
    assert isinstance(group, RoleGroupConstraint)
    assert group.filters == (OWNER, ADMINISTRATOR, DEVELOPER)


def test_constraint_or_group_prepends():
    group = DEVELOPER | (OWNER | ADMINISTRATOR)
    assert isinstance(group, RoleGroupConstraint)
    assert group.filters == (DEVELOPER, OWNER, ADMINISTRATOR)


def test_group_or_group_merges():
    group = (OWNER | ADMINISTRATOR) | (MODERATOR | GUEST)
    assert isinstance(group, RoleGroupConstraint)
    assert group.filters == (OWNER, ADMINISTRATOR, MODERATOR, GUEST)


# --- update_handler_flags --------------------------------------------------


def test_single_constraint_flags():
    flags: dict = {}
    OWNER.update_handler_flags(flags)
    assert flags["raito__roles"] == [OWNER.filter.data]


def test_group_flags_collect_all_roles():
    flags: dict = {}
    (OWNER | ADMINISTRATOR | DEVELOPER).update_handler_flags(flags)
    collected = [role.slug for role in flags["raito__roles"]]
    assert collected == ["owner", "administrator", "developer"]


def test_flags_append_to_existing():
    flags: dict = {"raito__roles": [GUEST.filter.data]}
    OWNER.update_handler_flags(flags)
    assert [role.slug for role in flags["raito__roles"]] == ["guest", "owner"]


# --- __call__ --------------------------------------------------------------


async def test_constraint_call_delegates_to_filter(raito, bot, make_message, make_user):
    user = make_user(user_id=555)
    await raito.role_manager.provider.set_role(bot.id, user.id, "owner")
    message = make_message(user=user)

    assert await OWNER(message, raito=raito, bot=bot) is True
    assert await ADMINISTRATOR(message, raito=raito, bot=bot) is False


async def test_group_call_true_when_user_has_any_member_role(raito, bot, make_message, make_user):
    user = make_user(user_id=777)
    await raito.role_manager.provider.set_role(bot.id, user.id, "administrator")
    message = make_message(user=user)

    group = OWNER | ADMINISTRATOR
    assert await group(message, raito=raito, bot=bot) is True


async def test_group_call_false_when_user_has_no_member_role(raito, bot, make_message, make_user):
    user = make_user(user_id=888)
    await raito.role_manager.provider.set_role(bot.id, user.id, "guest")
    message = make_message(user=user)

    group = OWNER | ADMINISTRATOR
    assert await group(message, raito=raito, bot=bot) is False


def test_constraint_wraps_role_filter():
    assert isinstance(OWNER, RoleConstraint)
    assert OWNER.filter.data.slug == "owner"
