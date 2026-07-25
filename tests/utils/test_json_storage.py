from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey

from raito.utils.storages.json import JSONStorage


def _key(bot_id=42, chat_id=1, user_id=2):
    return StorageKey(bot_id=bot_id, chat_id=chat_id, user_id=user_id)


async def test_set_and_get_state(tmp_path):
    storage = JSONStorage(tmp_path / "s.json")
    key = _key()
    assert await storage.get_state(key) is None
    await storage.set_state(key, "menu")
    assert await storage.get_state(key) == "menu"


async def test_set_state_accepts_state_object(tmp_path):
    storage = JSONStorage(tmp_path / "s.json")
    key = _key()
    state = State(state="form:name")
    await storage.set_state(key, state)
    # State objects are stored via their resolved ``.state`` string
    assert await storage.get_state(key) == state.state


async def test_set_and_get_data(tmp_path):
    storage = JSONStorage(tmp_path / "s.json")
    key = _key()
    assert await storage.get_data(key) == {}
    await storage.set_data(key, {"a": 1})
    assert await storage.get_data(key) == {"a": 1}


async def test_update_data_merges(tmp_path):
    storage = JSONStorage(tmp_path / "s.json")
    key = _key()
    await storage.set_data(key, {"a": 1})
    updated = await storage.update_data(key, {"b": 2})
    assert updated == {"a": 1, "b": 2}
    assert await storage.get_data(key) == {"a": 1, "b": 2}


async def test_persistence_across_instances(tmp_path):
    path = tmp_path / "s.json"
    key = _key()

    storage = JSONStorage(path)
    await storage.set_state(key, "active")
    await storage.set_data(key, {"n": 10})

    assert path.exists()

    reopened = JSONStorage(path)
    assert await reopened.get_state(key) == "active"
    assert await reopened.get_data(key) == {"n": 10}


async def test_keys_are_isolated(tmp_path):
    storage = JSONStorage(tmp_path / "s.json")
    key_a = _key(user_id=1)
    key_b = _key(user_id=2)
    await storage.set_state(key_a, "a")
    await storage.set_state(key_b, "b")
    assert await storage.get_state(key_a) == "a"
    assert await storage.get_state(key_b) == "b"


async def test_clear_removes_everything(tmp_path):
    path = tmp_path / "s.json"
    key = _key()
    storage = JSONStorage(path)
    await storage.set_state(key, "x")
    await storage.set_data(key, {"a": 1})

    await storage.clear()
    assert await storage.get_state(key) is None
    assert await storage.get_data(key) == {}

    # persisted as cleared
    reopened = JSONStorage(path)
    assert await reopened.get_state(key) is None
    assert await reopened.get_data(key) == {}


async def test_corrupted_file_is_ignored(tmp_path):
    path = tmp_path / "s.json"
    path.write_text("{not valid json", encoding="utf-8")
    storage = JSONStorage(path)
    assert await storage.get_state(_key()) is None
