import pytest
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey

from raito.utils.storages.sql.sqlite import SQLiteStorage


def _key(bot_id=42, chat_id=1, user_id=2):
    return StorageKey(bot_id=bot_id, chat_id=chat_id, user_id=user_id)


@pytest.fixture
async def storage():
    store = SQLiteStorage("sqlite+aiosqlite:///:memory:")
    await store.migrate()
    yield store
    await store.close()


async def test_empty_state_and_data(storage):
    key = _key()
    assert await storage.get_state(key) is None
    assert await storage.get_data(key) == {}


async def test_set_and_get_state(storage):
    key = _key()
    await storage.set_state(key, "active")
    assert await storage.get_state(key) == "active"


async def test_set_state_overwrites(storage):
    key = _key()
    await storage.set_state(key, "first")
    await storage.set_state(key, "second")
    assert await storage.get_state(key) == "second"


async def test_set_state_none_clears(storage):
    key = _key()
    await storage.set_state(key, "active")
    await storage.set_state(key, None)
    assert await storage.get_state(key) is None


async def test_set_and_get_data(storage):
    key = _key()
    await storage.set_data(key, {"x": 10})
    assert await storage.get_data(key) == {"x": 10}


async def test_set_data_replaces(storage):
    key = _key()
    await storage.set_data(key, {"x": 10})
    await storage.set_data(key, {"y": 20})
    assert await storage.get_data(key) == {"y": 20}


async def test_update_data_merges(storage):
    key = _key()
    await storage.set_data(key, {"x": 10})
    updated = await storage.update_data(key, {"y": 20})
    assert updated == {"x": 10, "y": 20}
    assert await storage.get_data(key) == {"x": 10, "y": 20}


async def test_keys_are_isolated(storage):
    key_a = _key(user_id=1)
    key_b = _key(user_id=2)
    await storage.set_state(key_a, "a")
    await storage.set_state(key_b, "b")
    assert await storage.get_state(key_a) == "a"
    assert await storage.get_state(key_b) == "b"
