🎬 Scenes
=========

A ``Scene`` is a multi-step dialog where every user message is handled by a new,
ordinary aiogram handler. It is the preferred choice for dialogs that use
request-scoped dependencies such as an SQLAlchemy ``AsyncSession``.

Unlike :doc:`conversations`, a scene does not suspend the handler that started
the dialog. It stores a small typed draft in FSM storage, returns from the
update, and resumes on the next matching update. Your usual middleware therefore
closes a database session, transaction, or other scoped resource after every
step — nothing is held while the user is away.

Scenes are built on aiogram's native ``StatesGroup``: each step is a real FSM
state, so ``StateFilter`` and any FSM tooling see it like any other state.

--------

Example
-------

.. code-block:: python

    from aiogram import F, filters
    from aiogram.fsm.state import State, StatesGroup
    from aiogram.types import Message
    from sqlalchemy.ext.asyncio import AsyncSession

    from raito import Router
    from raito.plugins.scenes import Scene, SceneData

    router = Router(name="moderation")


    class MuteData(SceneData):
        username: str | None = None
        minutes: int | None = None


    class MuteStates(StatesGroup):
        username = State()
        minutes = State()


    mute = router.scene(MuteStates, data=MuteData)


    @mute.on_message.enter(filters.Command("mute"))
    async def start(message: Message, scene: Scene[MuteData]) -> None:
        await message.answer("Enter username:")
        await scene.next()


    @mute.on_message(MuteStates.username, F.text)
    async def set_username(message: Message, scene: Scene[MuteData]) -> None:
        if not (message.text or "").startswith("@"):
            await message.answer("⚠️ Enter an @username")
            return await scene.retry()

        scene.data.username = message.text
        await message.answer("Enter duration in minutes:")
        await scene.next()


    @mute.on_message(MuteStates.minutes, F.text)
    async def set_minutes(
        message: Message,
        scene: Scene[MuteData],
        session: AsyncSession,
    ) -> None:
        if not (message.text or "").isdigit() or int(message.text) <= 0:
            await message.answer("⚠️ Enter a positive whole number")
            return await scene.retry()

        scene.data.minutes = int(message.text)
        await mute_user(session, scene.data.username, scene.data.minutes)
        await message.answer("✅ User muted")
        await scene.finish()

``session`` above is injected by the application's usual aiogram middleware. It
is fresh for the ``minutes`` update and is closed when that handler returns. A
scene never stores the session, a message, an ORM object, or a future.

--------

The ``scene`` handle
--------------------

Every handler may receive a ``scene: Scene[MuteData]`` parameter — a live handle
to the current update. It carries two things:

- ``scene.data`` — the typed, **mutable** draft. Assign to it directly
  (``scene.data.username = ...``); the change is validated immediately and
  snapshotted into FSM storage on the next navigation.
- navigation verbs that persist the draft and switch the FSM state:

  - ``await scene.next()`` — move to the next step in declaration order (or the
    first step, when called from an entry handler).
  - ``await scene.back()`` — move to the previous step.
  - ``await scene.goto(state)`` — jump to a specific step (branching).
  - ``await scene.retry()`` — stay on the current step; saves the draft.
  - ``await scene.restart()`` — discard the draft and start this scene over.
  - ``await scene.finish()`` / ``await scene.cancel()`` — end the scene, clearing
    only its own FSM payload.
  - ``await scene.escape()`` — cancel the scene *and* let the update reach the next
    matching handler, instead of swallowing it. See :ref:`scenes-escaping`.
  - ``await scene.start(other, at=OtherStates.reason, **data)`` — hand the dialog
    off to another scene, seeding its draft from ``data`` (validated against its
    ``SceneData``). Opens at ``other``'s first step, or ``at`` if given.

Navigation never sends anything. Reply with the message you already have —
``await message.answer(...)`` — which exposes every Telegram option natively
(``reply_markup``, ``parse_mode``, media, and so on). A typical step answers,
then navigates:

.. code-block:: python

    await message.answer("Enter minutes:", reply_markup=cancel_keyboard)
    await scene.next()

``scene.data`` is a Pydantic ``SceneData`` model used only as a typed,
JSON-serialisable draft. Give every field a default because a scene starts from
an empty draft. Build and validate a final domain command in the last step
rather than putting dependency-aware validators on ``SceneData``.

If a step does not touch the draft, ``scene: Scene`` (without ``[MuteData]``) is
enough. A handler may also declare ``state: FSMContext`` alongside ``scene`` for
raw FSM access — the handle does not get in the way.

--------

Events
------

Handlers are registered through the per-event decorators ``scene.on_message``,
``scene.on_callback_query``, and ``scene.on_edited_message`` — the ``on_`` prefix
mirrors Raito's ``router.on_pagination``. Each one is called with a step's state to
handle that step, and has an ``.enter`` to start the scene. So a scene can begin on
a command *or* a button, and any step can expect text *or* an inline button:

.. code-block:: python

    from aiogram.types import CallbackQuery
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    @mute.on_message.enter(filters.Command("mute"))       # start on a command
    async def start(message: Message, scene: Scene[MuteData]) -> None:
        await message.answer("Enter username:")
        await scene.next()


    @mute.on_message(MuteStates.username, F.text)
    async def set_username(message: Message, scene: Scene[MuteData]) -> None:
        scene.data.username = message.text

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Confirm", callback_data="confirm")
        keyboard.button(text="Cancel", callback_data="cancel")

        await message.answer("Mute this user?", reply_markup=keyboard.as_markup())
        await scene.next()


    @mute.on_callback_query(MuteStates.confirm, F.data == "confirm")   # handle a tap
    async def confirm(callback_query: CallbackQuery, scene: Scene[MuteData]) -> None:
        await callback_query.message.edit_text("✅ Muted")
        await scene.finish()

Each handler receives the same ``scene`` handle plus its event under the
observer's name — ``message``, ``callback_query``, or ``edited_message``, matching
the parameter name exactly, the same rule a plain ``@router.callback_query()``
handler already follows. Its middleware runs on every supported observer, so a
stale scene is cleared whether the next step expects text or a tap.
``scene.on_message``, ``scene.on_callback_query``, and ``scene.on_edited_message``
cover the events that carry a per-user FSM state.

Besides a specific step, each registrar also has ``.any(*filters)``, which matches
*any* active step of the scene — for something that should work no matter where
the user is, such as a persistent "Cancel" button or a ``/cancel`` command:

.. code-block:: python

    @mute.on_message.any(filters.Command("cancel"))
    async def cancel_anywhere(scene: Scene[MuteData]) -> None:
        await scene.cancel()

Like every scene handler, ``.any()`` still competes on **declaration order**: a
broad step filter (``F.text``) registered *before* it will match first and the
``.any()`` handler never runs. Declare scene-wide ``.any()`` handlers before the
steps they are meant to intercept.

--------

.. _scenes-escaping:

Handling an unrelated command
------------------------------

A scene's steps are ordinary handlers filtered by state, not by what the message
*looks like*. A step registered with a broad filter like ``F.text`` matches
literally any text — including ``/start`` or any other command the user sends
mid-dialog. FSM does not fix this by itself: without an explicit escape route, the
message is validated as if it were an answer to the current step (and, since
scenes have no built-in timeout, the user has no other way out until the dialog
finishes).

Give a scene an escape route with :meth:`SceneRegistry.any` and
:meth:`Scene.escape`:

.. code-block:: python

    @mute.on_message.any(F.text.startswith("/"))
    async def escape_on_any_command(scene: Scene[MuteData]) -> None:
        await scene.escape()

``scene.cancel()`` alone would still swallow the update — nothing else gets a turn
at it. ``scene.escape()`` clears the scene and then re-raises so aiogram keeps
looking for a match, exactly as if this handler had never matched. A real
``/start`` handler registered after this one still runs for the very same update,
so escaping a scene and getting the command's usual result is one step, not two.

--------

Storage and routing
--------------------

- Scenes use the injected ``FSMContext`` and therefore the storage configured on
  ``Dispatcher(storage=...)``. ``Raito.storage`` is separate and is not the scene
  store.
- Scene steps are ordinary message handlers, matched in **declaration order**
  like any aiogram handler. Declare a scene's handlers before a broad
  ``@router.message()`` catch-all on the same router, or — as in the example —
  keep the scene on its own router. Across routers, control priority with include
  order or Raito's ``Router(priority=...)``.
- Hot reload is otherwise transparent: aiogram identifies a step by name
  (``"MuteStates:username"``), not by the Python class object, so reloading a
  handler's *body* never disturbs a user mid-scene. Only removing or renaming a
  ``State`` does — the next message for that user clears the stale scene and
  continues through normal routing, logged at ``DEBUG`` on
  ``raito.plugins.scenes``.
- Each scene owns the FSM state for its chat/user while active. Do not mix it with
  unrelated aiogram FSM states or ``raito.wait_for`` for the same key. A router
  rejects two scenes over the same ``StatesGroup``.
- ``finish`` and ``cancel`` remove only the scene's own FSM payload. Other data
  stored under the same ``FSMContext`` key is preserved.
- There is only one FSM state per chat/user, so starting *any* scene — including
  re-entering the same one — replaces whatever was active before, silently and
  without warning. This is not a scenes quirk; the same is true of plain aiogram
  FSM. If accidentally abandoning one flow while starting another would be
  costly, guard the entry handler yourself:

  .. code-block:: python

      @mute.on_message.enter(filters.Command("mute"))
      async def start(scene: Scene[MuteData], state: FSMContext) -> None:
          raw_state = await state.get_state()
          if raw_state is not None and not mute.steps.owns(raw_state):
              await message.answer("Finish or /cancel your current action first.")
              return
          await scene.next()
