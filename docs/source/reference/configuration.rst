Configuration
=============

``Raito`` constructor
---------------------

.. code-block:: python

    Raito(
        dispatcher,
        routers_dir,
        *,
        developers=None,
        locales=None,
        production=True,
        enable_dangerous_commands=False,
        configuration=None,
        storage=None,
    )

=============================  =========================================================
Parameter                      Meaning
=============================  =========================================================
``dispatcher``                 The aiogram ``Dispatcher`` to drive.
``routers_dir``                Directory scanned for handler files.
``developers``                 User IDs that implicitly hold the ``developer`` role.
``locales``                    Locales for command registration (e.g. ``["en", "ru"]``).
``production``                 ``True`` disables the hot-reload watchdog.
``enable_dangerous_commands``  Allow ``.rt eval`` / ``.rt bash`` (arbitrary code). Off by default.
``configuration``              A :class:`~raito.utils.configuration.RaitoConfiguration` instance.
``storage``                    aiogram FSM storage; also selects the role backend.
=============================  =========================================================

Pass a :class:`~raito.utils.configuration.RaitoConfiguration` object to customise
pagination styling and the router list appearance, or to plug in a custom role
manager. See the :doc:`API reference <api>` for its fields.
