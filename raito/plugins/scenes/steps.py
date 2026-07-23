from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup

__all__ = ("SceneSteps",)


class SceneSteps:
    """The ordered steps of a scene, derived from an aiogram ``StatesGroup``.

    Owns everything about the step layout — the order used by ``scene.next`` and
    ``scene.back``, the membership checks that detect a stale scene, and the
    namespace prefix that tells a scene's own states apart from anything else in
    FSM storage.
    """

    def __init__(self, states: object) -> None:
        """Read the ordered steps out of a ``StatesGroup``.

        Typed as ``object`` because this is the runtime boundary: the public
        ``Router.scene`` types ``states`` as ``type[StatesGroup]``, but a dynamic
        caller can still pass anything, so the class is validated here.

        :param states: ``StatesGroup`` whose states are the scene's steps, in order
        :raises TypeError: if ``states`` is not a ``StatesGroup`` subclass
        :raises ValueError: if ``states`` declares no states
        """
        if not (isinstance(states, type) and issubclass(states, StatesGroup)):
            msg = "Scene states must be a StatesGroup subclass."
            raise TypeError(msg)

        if not states.__states__:
            msg = f"StatesGroup {states.__full_group_name__!r} declares no states."
            raise ValueError(msg)

        self.id = states.__full_group_name__
        self.prefix = f"{self.id}:"
        self.states = states.__states__
        self._names = frozenset(states.__state_names__)
        self._index = {state.state: position for position, state in enumerate(self.states)}

    def owns(self, raw_state: str) -> bool:
        """Whether ``raw_state`` lives in this scene's namespace (current or removed)."""
        return raw_state.startswith(self.prefix)

    def is_active(self, raw_state: str) -> bool:
        """Whether ``raw_state`` is a step this scene still declares."""
        return raw_state in self._names

    def ensure(self, state: State) -> None:
        """Validate that ``state`` is a step of this scene.

        :param state: state to check
        :raises ValueError: if ``state`` is not one of the scene's steps
        """
        if not isinstance(state, State) or state.state not in self._names:
            msg = f"{state!r} is not a step of scene {self.id!r}."
            raise ValueError(msg)

    def step_for(self, raw_state: str) -> State:
        """Return the step matching ``raw_state``.

        Trusts that ``raw_state`` is already an active step of this scene — the
        ``StateFilter`` that matched the handler already established that.

        :param raw_state: state aiogram already resolved for this update
        :return: the matching step
        """
        return self.states[self._index[raw_state]]

    def after(self, step: State | None) -> State:
        """Return the step following ``step`` (the first step, from entry).

        :param step: current step, or ``None`` at entry
        :return: next step in declaration order
        :raises RuntimeError: if ``step`` is already the last step
        """
        position = 0 if step is None else self._index[step.state] + 1
        if position >= len(self.states):
            msg = f"Scene {self.id!r}: no step after {step!r}; call scene.finish()."
            raise RuntimeError(msg)

        return self.states[position]

    def before(self, step: State | None) -> State:
        """Return the step preceding ``step``.

        :param step: current step
        :return: previous step in declaration order
        :raises RuntimeError: if there is no earlier step
        """
        position = -1 if step is None else self._index[step.state] - 1
        if position < 0:
            msg = f"Scene {self.id!r}: no step before {step!r}."
            raise RuntimeError(msg)

        return self.states[position]
