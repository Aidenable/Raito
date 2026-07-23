from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, NoReturn

from aiogram.dispatcher.event.bases import SkipHandler

from .data import TSceneData

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State

    from .manager import SceneManager

__all__ = ("Scene",)


class Scene(Generic[TSceneData]):
    """Per-update handle to an active scene, injected into every handler as ``scene``.

    Carries the typed draft (:attr:`data`) and the verbs to move between steps. One
    instance is built per update and discarded when the handler returns, so it never
    outlives a single message nor holds a resource.

    Navigation only changes state: it saves the draft and switches the FSM step. It
    never sends anything — reply with the message you already have
    (``await message.answer(...)``), which exposes every Telegram option natively.
    """

    __slots__ = ("_base", "_manager", "_state", "_step", "data")

    def __init__(
        self,
        manager: SceneManager[TSceneData],
        state: FSMContext,
        *,
        data: TSceneData,
        step: State | None,
        base: dict[str, Any] | None,
    ) -> None:
        """Initialize the scene handle.

        :param manager: scene this handle belongs to
        :param state: FSM context for the current chat/user
        :param data: typed draft, rehydrated from storage (or empty at entry)
        :param step: current step, or ``None`` inside an entry handler
        :param base: FSM data already read for this update, reused when persisting
        """
        self.data = data
        self._manager = manager
        self._state = state
        self._step = step
        self._base = base

    async def goto(self, target: State) -> None:
        """Save the draft and switch to ``target``.

        :param target: step to activate next
        :raises ValueError: if ``target`` is not a step of this scene
        """
        self._manager.steps.ensure(target)
        await self._manager.persist(self._state, self.data, self._base)
        await self._state.set_state(target)

    async def next(self) -> None:
        """Save the draft and advance to the next step (the first one, from entry)."""
        await self.goto(self._manager.steps.after(self._step))

    async def back(self) -> None:
        """Save the draft and return to the previous step."""
        await self.goto(self._manager.steps.before(self._step))

    async def retry(self) -> None:
        """Stay on the current step, saving the draft."""
        await self._manager.persist(self._state, self.data, self._base)

    async def finish(self) -> None:
        """End the scene, clearing only its own FSM payload."""
        await self._manager.clear(self._state, self._base)

    async def cancel(self) -> None:
        """Alias of :meth:`finish` for an explicit cancellation path."""
        await self.finish()

    async def escape(self) -> NoReturn:
        """Cancel the scene and let this update reach the next matching handler.

        Use this to let an unrelated command interrupt the scene, e.g. ``/start``
        arriving mid-dialog. Combine with :meth:`SceneRegistry.any` to catch it
        regardless of which step the user is on:

        .. code-block:: python

            @mute.on_message.any(F.text.startswith("/"))
            async def escape_on_any_command(scene: Scene[MuteData]) -> None:
                await scene.escape()

        A plain :meth:`cancel` would still swallow the update — nothing else gets a
        turn at it. ``escape`` clears the scene, then re-raises so aiogram keeps
        looking, exactly as if this handler had never matched (a real ``/start``
        handler registered after this one still runs for the same update).
        """
        await self.cancel()
        raise SkipHandler

    async def restart(self) -> None:
        """Discard the current draft and start this scene over from its first step."""
        await self._manager.begin(self._state, self._base, {})

    async def start(
        self,
        target: SceneManager[Any],
        *,
        at: State | None = None,
        **data: object,
    ) -> None:
        """End this scene and start ``target``, seeding its draft from ``data``.

        The current payload is replaced by a fresh draft for ``target``, validated
        against its ``SceneData``. Send the target's first prompt yourself, as with
        any navigation.

        :param target: scene to hand the dialog off to
        :param at: step to open ``target`` at; defaults to its first step
        :param data: initial fields for the target's draft
        :raises ValueError: if ``at`` is not a step of ``target``
        """
        await target.begin(self._state, self._base, data, at=at)
