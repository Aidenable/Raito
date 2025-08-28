🔁 retry
=============================

Retries a coroutine if Telegram raises ``RetryAfter``.

.. code-block:: python

   from raito import rt

   await rt.retry(bot.send_message(...))

---------

Arguments:

- ``max_attempts`` – total number of tries (default: 5)
- ``additional_delay`` – extra seconds to wait beyond ``retry_after``
