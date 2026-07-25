📝 Logging
==========

Raito ships a colored, adaptive log formatter so your terminal output is
readable out of the box.

Enable it
---------

:meth:`~raito.Raito.init_logging` installs the formatter on the root logger:

.. code-block:: python

    raito = Raito(dispatcher, "handlers", production=False)
    raito.init_logging()

The level follows ``production``: ``DEBUG`` in development, ``INFO`` in
production. Pass logger names to silence noisy third-party loggers:

.. code-block:: python

    raito.init_logging("aiogram.event", "aiogram.dispatcher")

Each name is dropped via a :class:`~raito.utils.loggers.MuteLoggersFilter`.

What you get
------------

- **Level-colored tags** — ``D / I / W / E / C`` on a colored background.
- **Adaptive timestamps** — :class:`~raito.utils.loggers.ColoredFormatter` shows
  more (date, logger name) on wide terminals and less on narrow ones, so lines
  don't wrap.
- Warnings are captured into logging (``logging.captureWarnings(True)``), so
  ``DeprecationWarning`` and friends appear in your logs too.

Logging from your code
----------------------

The ``rt`` namespace exposes the root logger and a ``debug`` shortcut:

.. code-block:: python

    from raito import rt

    rt.debug("Loaded %d items", count)     # rt.log.debug
    rt.log.info("Hello, %s", name)
    rt.log.warning("Careful")
    rt.log.error("Something failed")

Raito's own subsystems log under named loggers (``raito.core``,
``raito.routers``, ``raito.roles``, ``raito.scenes``, …), so you can tune or mute
any part independently.
