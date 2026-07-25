"""Tests for RoleFilter event resolution and role checking."""

from __future__ import annotations

import pytest
from aiogram.types import TelegramObject

from raito.rt import ADMINISTRATOR, OWNER
from raito.plugins.roles.filter import RoleFilter


async def test_filter_matches_assigned_role(raito, bot, make_message, make_user):
    user = make_user(user_id=321)
    await raito.role_manager.provider.set_role(bot.id, user.id, "owner")
    message = make_message(user=user)

    assert await OWNER.filter(message, raito=raito, bot=bot) is True


async def test_filter_rejects_other_role(raito, bot, make_message, make_user):
    user = make_user(user_id=321)
    await raito.role_manager.provider.set_role(bot.id, user.id, "owner")
    message = make_message(user=user)

    assert await ADMINISTRATOR.filter(message, raito=raito, bot=bot) is False


async def test_filter_false_when_no_role(raito, bot, make_message, make_user):
    user = make_user(user_id=654)
    message = make_message(user=user)

    assert await OWNER.filter(message, raito=raito, bot=bot) is False


async def test_filter_works_via_role_manager_assignment(raito, bot, make_message, make_user):
    initiator = make_user(user_id=1)
    target = make_user(user_id=2)
    await raito.role_manager.provider.set_role(bot.id, initiator.id, "owner")
    await raito.role_manager.assign_role(
        bot.id, initiator_id=initiator.id, target_id=target.id, role_slug="administrator"
    )
    message = make_message(user=target)

    assert await ADMINISTRATOR.filter(message, raito=raito, bot=bot) is True
    assert await OWNER.filter(message, raito=raito, bot=bot) is False


async def test_filter_raises_without_from_user(raito, bot):
    event = TelegramObject()  # no from_user attribute
    with pytest.raises(TypeError):
        await OWNER.filter(event, raito=raito, bot=bot)


async def test_filter_matches_on_callback_query(raito, bot, make_callback_query, make_user):
    user = make_user(user_id=999)
    await raito.role_manager.provider.set_role(bot.id, user.id, "administrator")
    callback = make_callback_query(user=user)

    assert await ADMINISTRATOR.filter(callback, raito=raito, bot=bot) is True


def test_from_data_roundtrip():
    original = OWNER.filter
    clone = RoleFilter.from_data(original.data)
    assert clone.data == original.data
