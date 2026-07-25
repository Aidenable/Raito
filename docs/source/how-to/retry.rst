🔁 retry
=============================

Calls an async function and retries it when Telegram raises a transient error —
flood control (``RetryAfter``) or a network/server error
(``TelegramNetworkError``, ``TelegramServerError``).

Pass the coroutine **function** (or bound method) and its arguments — not an
already-created coroutine. ``retry`` re-invokes the function on every attempt,
and your IDE checks the argument names and types just like a direct call:

.. code-block:: python

   from raito import rt

   await rt.retry(bot.send_message, chat_id, "...")
   await rt.retry(message.answer, "...")

.. deprecated:: 1.6.0

   Do **not** call the function yourself. ``rt.retry(bot.send_message(...))``
   still works but emits a ``DeprecationWarning`` (and your type checker flags
   it): the resulting coroutine is awaited only once and cannot be retried.
   Support will be removed in 1.8.0.

Retries use a fixed policy — up to 5 attempts, honouring the server-provided
``retry_after`` for flood control and exponential backoff for network/server
errors.
