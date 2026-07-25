"""Tests for :class:`raito.core.routers.router.Router`."""

from __future__ import annotations

import pytest
from aiogram.fsm.state import State, StatesGroup

from raito import Router
from raito.plugins.scenes import SceneData, SceneManager


class _ExampleStates(StatesGroup):
    first = State()
    second = State()


class _OtherStates(StatesGroup):
    only = State()


class _ExampleData(SceneData):
    pass


def test_router_defaults():
    router = Router()

    assert router.priority == 0
    assert router.autoload is True


def test_router_explicit_values():
    router = Router(name="custom", priority=5, autoload=False)

    assert router.name == "custom"
    assert router.priority == 5
    assert router.autoload is False


def test_scene_creates_scene_manager():
    router = Router(name="scened")

    scene = router.scene(_ExampleStates, data=_ExampleData)

    assert isinstance(scene, SceneManager)


def test_scene_without_data_uses_default():
    router = Router(name="scened")

    scene = router.scene(_ExampleStates)

    assert isinstance(scene, SceneManager)


def test_scene_duplicate_states_raises():
    router = Router(name="scened")
    router.scene(_ExampleStates, data=_ExampleData)

    with pytest.raises(ValueError):
        router.scene(_ExampleStates, data=_ExampleData)


def test_scene_different_states_allowed():
    router = Router(name="scened")

    first = router.scene(_ExampleStates)
    second = router.scene(_OtherStates)

    assert isinstance(first, SceneManager)
    assert isinstance(second, SceneManager)
