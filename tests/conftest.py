"""Shared fixtures for the test suite."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Chat, Message, User

from raito import Raito

from .mocked_bot import MockedBot

_DATE = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)


@pytest.fixture
def bot() -> MockedBot:
    return MockedBot()


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture
def dispatcher(storage: MemoryStorage) -> Dispatcher:
    return Dispatcher(storage=storage)


@pytest.fixture
def raito(dispatcher: Dispatcher, storage: MemoryStorage, tmp_path) -> Raito:
    return Raito(dispatcher, str(tmp_path), storage=storage)


@pytest.fixture
def make_user() -> Callable[..., User]:
    def _make(user_id: int = 12345, **kwargs) -> User:
        kwargs.setdefault("is_bot", False)
        kwargs.setdefault("first_name", "Test")
        return User(id=user_id, **kwargs)

    return _make


@pytest.fixture
def make_chat() -> Callable[..., Chat]:
    def _make(chat_id: int = 12345, chat_type: str = "private", **kwargs) -> Chat:
        return Chat(id=chat_id, type=chat_type, **kwargs)

    return _make


@pytest.fixture
def make_message(make_user, make_chat) -> Callable[..., Message]:
    def _make(
        text: str = "/cmd", *, user: User | None = None, chat: Chat | None = None, **kwargs
    ) -> Message:
        return Message(
            message_id=1,
            date=_DATE,
            chat=chat or make_chat(),
            from_user=make_user() if user is None else user,
            text=text,
            **kwargs,
        )

    return _make


@pytest.fixture
def make_callback_query(make_user, make_message) -> Callable[..., CallbackQuery]:
    def _make(
        data: str = "cb", *, user: User | None = None, message: Message | None = None, **kwargs
    ) -> CallbackQuery:
        return CallbackQuery(
            id="1",
            from_user=make_user() if user is None else user,
            chat_instance="1",
            message=message or make_message(),
            data=data,
            **kwargs,
        )

    return _make
