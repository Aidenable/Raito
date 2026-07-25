"""Tests for :class:`raito.plugins.scenes.steps.SceneSteps`."""

from __future__ import annotations

import pytest
from aiogram.fsm.state import State, StatesGroup

from raito.plugins.scenes.steps import SceneSteps


class S(StatesGroup):
    a = State()
    b = State()


@pytest.fixture
def steps() -> SceneSteps:
    return SceneSteps(S)


def test_reads_group_metadata(steps: SceneSteps) -> None:
    assert steps.id == S.__full_group_name__
    assert steps.prefix == f"{S.__full_group_name__}:"
    assert steps.states == S.__states__


def test_owns_matches_namespace_prefix(steps: SceneSteps) -> None:
    assert steps.owns(S.a.state) is True
    assert steps.owns(S.b.state) is True
    # A removed step still lives in the namespace.
    assert steps.owns(f"{S.__full_group_name__}:removed") is True
    assert steps.owns("Other:a") is False


def test_is_active_only_for_declared_steps(steps: SceneSteps) -> None:
    assert steps.is_active(S.a.state) is True
    assert steps.is_active(S.b.state) is True
    assert steps.is_active(f"{S.__full_group_name__}:gone") is False
    assert steps.is_active("Other:a") is False


def test_step_for_returns_matching_state(steps: SceneSteps) -> None:
    assert steps.step_for(S.a.state) is S.a
    assert steps.step_for(S.b.state) is S.b


def test_after_none_returns_first_step(steps: SceneSteps) -> None:
    assert steps.after(None) is S.a


def test_after_returns_next_step(steps: SceneSteps) -> None:
    assert steps.after(S.a) is S.b


def test_after_last_step_raises(steps: SceneSteps) -> None:
    with pytest.raises(RuntimeError):
        steps.after(S.b)


def test_before_returns_previous_step(steps: SceneSteps) -> None:
    assert steps.before(S.b) is S.a


def test_before_first_step_raises(steps: SceneSteps) -> None:
    with pytest.raises(RuntimeError):
        steps.before(S.a)


def test_ensure_accepts_own_step(steps: SceneSteps) -> None:
    # Does not raise for a declared step.
    steps.ensure(S.a)


def test_ensure_rejects_foreign_state(steps: SceneSteps) -> None:
    with pytest.raises(ValueError):
        steps.ensure(State())


def test_non_states_group_raises_type_error() -> None:
    class NotAGroup:
        pass

    with pytest.raises(TypeError):
        SceneSteps(NotAGroup)

    with pytest.raises(TypeError):
        SceneSteps("not a group")


def test_empty_group_raises_value_error() -> None:
    class Empty(StatesGroup):
        pass

    with pytest.raises(ValueError):
        SceneSteps(Empty)
