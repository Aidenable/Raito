from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram.dispatcher.flags import extract_flags_from_object
from aiogram.filters import StateFilter

if TYPE_CHECKING:
    from collections.abc import Callable

    from aiogram.dispatcher.event.handler import CallbackType
    from aiogram.dispatcher.event.telegram import TelegramEventObserver
    from aiogram.fsm.state import State

    from .manager import SceneManager
    from .middleware import SceneMiddleware

__all__ = ("SceneRegistry",)


class SceneRegistry:
    """Registers a scene's handlers for one aiogram event type.

    A scene exposes one of these per event as ``scene.on_message``,
    ``scene.on_callback_query``, and ``scene.on_edited_message``. Call it with a
    step's state to handle that step, use :meth:`any` for a handler that runs on
    every step, or use :meth:`enter` to start the scene. Its :class:`SceneMiddleware`
    is installed on the observer only when the first handler is added, so an event
    type without scene handlers is never touched.
    """

    def __init__(
        self,
        scene: SceneManager[Any],
        observer: TelegramEventObserver,
        name: str,
        middleware: SceneMiddleware,
    ) -> None:
        """Bind the registry to one observer of the scene's router.

        :param scene: scene the handlers belong to
        :param observer: aiogram event observer to register on
        :param name: event name, also the handler's event argument
        :param middleware: middleware installed on first registration
        """
        self._scene = scene
        self._observer = observer
        self._name = name
        self._middleware = middleware
        self._installed = False

    def __call__(
        self, state: State, *filters: CallbackType
    ) -> Callable[[CallbackType], CallbackType]:
        """Register a handler for the ``state`` step.

        :param state: step to handle, a state of the scene's ``StatesGroup``
        :param filters: extra filters applied on top of the step's state
        :return: decorator for the step handler
        :raises ValueError: if ``state`` is not a step of this scene
        """
        self._scene.steps.ensure(state)
        return self._register((StateFilter(state), *filters), entry=False)

    def any(self, *filters: CallbackType) -> Callable[[CallbackType], CallbackType]:
        """Register a handler that runs on any active step of this scene.

        Useful for something that should work no matter where the user is in the
        dialog, e.g. a ``/cancel`` command or a persistent "Cancel" button:

        .. code-block:: python

            @mute.on_message.any(filters.Command("cancel"))
            async def cancel_anywhere(scene: Scene[MuteData]) -> None:
                await scene.cancel()

        :param filters: filters applied on top of "any step of this scene"
        :return: decorator for the handler
        """
        return self._register((StateFilter(*self._scene.steps.states), *filters), entry=False)

    def enter(self, *filters: CallbackType) -> Callable[[CallbackType], CallbackType]:
        """Register a handler that starts the scene from a fresh draft.

        :param filters: filters that trigger the scene, e.g. ``Command("mute")``
        :return: decorator for the entry handler
        """
        return self._register(filters, entry=True)

    def _register(
        self,
        filters: tuple[CallbackType, ...],
        *,
        entry: bool,
    ) -> Callable[[CallbackType], CallbackType]:
        if not self._installed:
            self._observer.outer_middleware(self._middleware)
            self._installed = True

        def decorator(callback: CallbackType) -> CallbackType:
            handler = self._scene.build_handler(callback, self._name, entry=entry)
            self._observer.register(handler, *filters, flags=extract_flags_from_object(callback))
            return callback

        return decorator
