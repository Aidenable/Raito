Scenes vs. conversations
========================

Raito has two ways to run a multi-step dialog. They look similar but make
opposite trade-offs around **request-scoped dependencies**. Choosing correctly
is mostly about how your app provides things like database sessions.

The core difference
-------------------

A **scene** never suspends the handler that started it. Each step is a separate,
fully-returning handler. Between steps the dialog's state lives in FSM storage,
and the coroutine is gone — so any per-update dependency your middleware provides
(a session, a transaction, an open file) is set up and **torn down around every
step**, exactly as for a normal message.

A **conversation** (``wait_for``) does the opposite: it *suspends* the current
handler coroutine until the next matching message arrives. The handler stays
alive the whole time the user is thinking, which means anything it holds — the
session it was given for this update, objects bound to it — stays alive too.

.. code-block:: text

    Scene:         msg1 → [handler runs, returns] … msg2 → [fresh handler runs, returns]
                   dependencies released between steps

    Conversation:  msg1 → [handler suspends on wait_for] ……… msg2 → [handler resumes]
                   dependencies held for the whole wait

Why it matters
--------------

If a step needs a database session and you use a per-update session middleware
(the common SQLAlchemy pattern), a scene gives each step a **fresh** session and
returns it to the pool while the user types. A conversation would keep one
session checked out for the entire dialog — fine for a quick two-message
exchange, wasteful (and a pool-exhaustion risk) for anything longer.

How each is built
-----------------

**Scenes** are built on aiogram's ``StatesGroup``: each step is a real FSM state,
and a small typed :class:`~raito.plugins.scenes.SceneData` draft is stored under
the FSM key. Navigation (``scene.next()`` / ``finish()`` / …) just persists the
draft and switches the state string; nothing is held in memory.

**Conversations** use an ``asyncio.Future``: ``wait_for`` registers a future,
sets a marker FSM state, and awaits it. A middleware resolves the future when the
next message passes your filters, resuming the suspended coroutine.

When to reach for which
-----------------------

Prefer a **scene** when:

- a step touches request-scoped resources (DB sessions, transactions);
- the dialog has more than a couple of steps, branches, or a cancel path;
- you want each step to be an ordinary, testable handler.

A **conversation** is fine when:

- the wait is short and the handler holds nothing expensive;
- you want the simplest possible "ask one question and continue" inline in a
  handler.

See the :doc:`scenes <../how-to/scenes>` and
:doc:`conversations <../how-to/conversations>` how-to guides for the APIs.
