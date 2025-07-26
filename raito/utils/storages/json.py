from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey
from typing_extensions import override

from raito.utils import loggers

__all__ = ("JSONStorage",)


class JSONStorage(BaseStorage):
    """JSON-based FSM storage for development and testing.

    Stores FSM state and data in a local JSON file as a flat key-value mapping.
    """

    def __init__(self, path: str | Path, *, key_separator: str = ":") -> None:
        """Initialize JSONStorage.

        :param path: Path to the JSON file to be used for persistent storage
        :param key_separator: Delimiter used when constructing keys
        """
        self.path = Path(path)
        self.key_separator = key_separator

        self._data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load JSON file contents into memory."""
        if self.path.exists():
            try:
                content = self.path.read_text(encoding="utf-8")
                self._data = json.loads(content)
            except json.JSONDecodeError as exc:
                loggers.storages.warning("JSON decode error: %s — file will be ignored", exc)
                self._data = {}
            except UnicodeDecodeError as exc:
                loggers.storages.warning("Invalid encoding in %s: %s", self.path, exc)
                self._data = {}
            except OSError as exc:
                loggers.storages.warning("Failed to read JSON storage file: %s", exc)
                self._data = {}

    def _save(self) -> None:
        """Write current memory state to JSON file."""
        self.path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _build_key(self, key: StorageKey) -> str:
        """Construct a unique key string from StorageKey.

        :param key: FSM storage key
        :return: String key
        """
        parts = [str(key.bot_id), str(key.chat_id), str(key.user_id)]
        if key.thread_id:
            parts.append(str(key.thread_id))
        if key.business_connection_id:
            parts.append(str(key.business_connection_id))
        if key.destiny:
            parts.append(key.destiny)
        return self.key_separator.join(parts)

    @override
    async def get_state(self, key: StorageKey) -> str | None:
        """Retrieve the current state for a key.

        :param key: FSM storage key
        :return: Current state or None
        """
        return self._data.get(self._build_key(key), {}).get("state")

    @override
    async def set_state(self, key: StorageKey, state: StateType | None = None) -> None:
        """Set a new state for the given key.

        :param key: FSM storage key
        :param state: New state to store
        """
        if isinstance(state, State):
            state = state.state

        str_key = self._build_key(key)
        self._data.setdefault(str_key, {})["state"] = state
        self._save()

    @override
    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        """Retrieve data dictionary for the key.

        :param key: FSM storage key
        :return: Stored data or empty dict
        """
        return self._data.get(self._build_key(key), {}).get("data", {})

    @override
    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        """Set data dictionary for the key.

        :param key: FSM storage key
        :param data: Data to store
        """
        str_key = self._build_key(key)
        self._data.setdefault(str_key, {})["data"] = data
        self._save()

    @override
    async def update_data(self, key: StorageKey, data: Mapping[str, Any]) -> dict[str, Any]:
        """Update the current data for the key.

        :param key: FSM storage key
        :param data: New data to merge with existing
        :return: Updated data
        """
        current = await self.get_data(key)
        current.update(data)

        await self.set_data(key, current)
        return current

    async def clear(self) -> None:
        """Clear all states and data from storage."""
        self._data.clear()
        self._save()

    @override
    async def close(self) -> None:
        """Close the storage (optional flush)"""
        self._save()
