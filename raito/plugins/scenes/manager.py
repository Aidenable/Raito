from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic

from aiogram.dispatcher.event.handler import CallableObject
from pydantic import BaseModel, ConfigDict, ValidationError

from raito.utils import loggers

from .data import TSceneData
from .middleware import SceneMiddleware
from .registry import SceneRegistry
from .scene import Scene
from .steps import SceneSteps

if TYPE_CHECKING:
    from aiogram.dispatcher.event.handler import CallbackType
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
    from aiogram.types import TelegramObject

    from raito.core.routers.router import Router

__all__ = ("SceneManager",)

FSM_KEY = "raito__scene"


class _ScenePayload(BaseModel):
    """The wire format of a scene's FSM payload — JSON in, JSON out.

    ``scene`` is purely diagnostic (readable when inspecting raw storage); the FSM
    state string is what actually identifies the active scene and step.
    """

    model_config = ConfigDict(frozen=True)

    scene: str
    data: dict[str, Any]


class SceneManager(Generic[TSceneData]):
    """A scene: the steps of a ``StatesGroup``, its draft type, and its handlers.

    Returned by :meth:`raito.Router.scene`. Register handlers through the per-event
    registrars :attr:`on_message`, :attr:`on_callback_query`, :attr:`on_edited_message`
    — ``scene.on_message.enter(...)`` to start, ``scene.on_message(state, ...)`` /
    ``scene.on_callback_query(state, ...)`` for steps. A :class:`SceneMiddleware` calls
    :meth:`cleanup` before them to drop a stale scene, and each active handler
    receives a :class:`Scene` handle that persists the draft through
    :meth:`persist` / :meth:`clear`.
    """

    def __init__(
        self,
        router: Router,
        states: type[StatesGroup],
        data_type: type[TSceneData],
    ) -> None:
        """Initialize the scene and expose its per-event registrars.

        :param router: router the scene's handlers are registered on
        :param states: ``StatesGroup`` whose states are the scene's steps, in order
        :param data_type: ``SceneData`` subclass used for the typed draft
        :raises TypeError: if ``states`` is not a ``StatesGroup`` subclass
        :raises ValueError: if ``states`` is empty
        """
        self.steps = SceneSteps(states)
        self.id = self.steps.id
        self._data_type = data_type

        middleware = SceneMiddleware(self)
        self.on_message = SceneRegistry(self, router.message, "message", middleware)
        self.on_edited_message = SceneRegistry(
            self, router.edited_message, "edited_message", middleware
        )
        self.on_callback_query = SceneRegistry(
            self, router.callback_query, "callback_query", middleware
        )

    async def cleanup(self, state: FSMContext | None, raw_state: str | None) -> bool:
        """Clear the active scene if ``raw_state`` belongs to it but no longer exists.

        Cheap when the update is not sitting in this scene: it returns ``False``
        after a string check, without touching storage.

        :param state: FSM context for the current chat/user, if any
        :param raw_state: state aiogram already resolved for this update
        :return: whether a stale scene was cleared
        """
        if state is None or not raw_state or not self.steps.owns(raw_state):
            return False

        if not self.steps.is_active(raw_state):
            await self.clear(state, None)
            loggers.scenes.debug(
                "Cleared stale scene %r for %r: %r is no longer a step (hot reload?)",
                self.id,
                state.key,
                raw_state,
            )
            return True

        return False

    async def persist(
        self,
        state: FSMContext,
        draft: TSceneData,
        base: dict[str, Any] | None,
    ) -> None:
        """Snapshot the draft into FSM storage.

        :param state: FSM context for the current chat/user
        :param draft: draft to store
        :param base: FSM data already read this update, or ``None`` to read it now
        """
        data = base if base is not None else await state.get_data()
        payload = _ScenePayload(scene=self.id, data=draft.model_dump(mode="json"))

        data[FSM_KEY] = payload.model_dump(mode="json")
        await state.set_data(data)

    async def clear(self, state: FSMContext, base: dict[str, Any] | None) -> None:
        """Remove only this scene's payload and reset the FSM state.

        :param state: FSM context for the current chat/user
        :param base: FSM data already read this update, or ``None`` to read it now
        """
        data = base if base is not None else await state.get_data()

        data.pop(FSM_KEY, None)
        await state.set_data(data)
        await state.set_state(None)

    async def begin(
        self,
        state: FSMContext,
        base: dict[str, Any] | None,
        data: dict[str, object],
        *,
        at: State | None = None,
    ) -> None:
        """Seed a fresh draft for this scene and switch to a step.

        Used by :meth:`Scene.start` and :meth:`Scene.restart` to (re)enter
        a scene; it replaces whatever scene payload is currently stored under the FSM
        key.

        :param state: FSM context for the current chat/user
        :param base: FSM data already read this update, or ``None`` to read it now
        :param data: initial fields for the draft, validated against the ``SceneData``
        :param at: step to open at; defaults to the first step
        :raises ValueError: if ``at`` is not a step of this scene
        """
        if at is not None:
            self.steps.ensure(at)

        draft = self._data_type(**data)

        await self.persist(state, draft, base)
        await state.set_state(at if at is not None else self.steps.after(None))

    def build_handler(
        self,
        callback: CallbackType,
        event_name: str,
        *,
        entry: bool,
    ) -> CallbackType:
        """Wrap a user callback into a scene handler.

        The wrapper hydrates the draft, builds the :class:`Scene` handle, and injects
        both the event (under ``event_name``) and ``scene`` into the callback. The
        current step is resolved from ``raw_state`` at call time rather than fixed at
        registration, so the same wrapper serves a specific step or :meth:`SceneRegistry.any`.

        :param callback: user handler
        :param event_name: name the event is passed under (``message``, ``callback_query``, ...)
        :param entry: whether this handler starts the scene from a fresh draft
        :return: the wrapped handler to register on an observer
        """
        user = CallableObject(callback)

        async def handler(
            event: TelegramObject,
            state: FSMContext,
            raw_state: str | None = None,
            **data: object,
        ) -> object:
            if entry:
                draft: TSceneData = self._data_type()
                base: dict[str, Any] | None = None
                step = None
            else:
                base = await state.get_data()
                try:
                    draft = self._load(base)
                except ValidationError as error:
                    await self.clear(state, base)
                    msg = f"Scene {self.id!r}: stored draft no longer matches {self._data_type.__name__}."
                    raise RuntimeError(msg) from error

                assert raw_state is not None, (
                    "a step handler's own StateFilter already matched raw_state"
                )
                step = self.steps.step_for(raw_state)

            scene: Scene[TSceneData] = Scene(self, state, data=draft, step=step, base=base)
            return await user.call(**{**data, event_name: event, "state": state, "scene": scene})

        return handler

    def _load(self, fsm_data: dict[str, Any]) -> TSceneData:
        payload = _ScenePayload.model_validate(fsm_data.get(FSM_KEY))
        return self._data_type.model_validate(payload.data)
