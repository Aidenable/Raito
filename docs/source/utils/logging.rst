📝 ColoredFormatter
=============================

Raito uses an adaptive logging for better terminal output.

Features:

- Colored tags based on log level
- Timestamps depending on terminal width
- Optional mute filter: ``MuteLoggersFilter``

To enable logging:

.. code-block:: python

   raito.init_logging("aiogram.event")

This replaces the root logger with color formatting and optional muted loggers.

Usage
~~~~~

.. code-block:: python

   from raito import rt

   rt.debug("Debug")

   rt.log.info("Hello, %s", "John")
   rt.log.warn("Warning")
   rt.log.error("Error")
