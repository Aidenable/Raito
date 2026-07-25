In-chat ``.rt`` commands
========================

Raito registers a set of built-in developer commands. They use the ``.rt``
prefix (a dot, ``rt`` and a space) instead of ``/`` and are **hidden** from the
Telegram slash menu — you invoke them by typing them in the chat.

Every command is gated by a role. The user must hold one of the listed roles
(or be a configured ``developer``).

Router management
-----------------

.. list-table::
    :header-rows: 1
    :widths: 34 26 40

    * - Command
      - Roles
      - Description
    * - ``.rt help``
      - DEVELOPER
      - Paginated list of all built-in commands.
    * - ``.rt routers``
      - DEVELOPER
      - Render the router tree with load status.
    * - ``.rt load <name>``
      - DEVELOPER
      - Load a router by name (e.g. an ``autoload=False`` one).
    * - ``.rt unload <name>``
      - DEVELOPER
      - Unload a router.
    * - ``.rt reload <name>``
      - DEVELOPER
      - Reload a router.

Roles
-----

.. list-table::
    :header-rows: 1
    :widths: 24 36 40

    * - Command
      - Roles
      - Description
    * - ``.rt roles``
      - DEVELOPER · OWNER · ADMINISTRATOR
      - Open a role picker, then assign to a user ID.
    * - ``.rt assign``
      - DEVELOPER · OWNER · ADMINISTRATOR
      - Alias of ``.rt roles``.
    * - ``.rt revoke``
      - DEVELOPER · OWNER · ADMINISTRATOR
      - Remove a user's role.
    * - ``.rt staff``
      - DEVELOPER · OWNER · ADMINISTRATOR
      - Tree of all users grouped by role.

System
------

.. list-table::
    :header-rows: 1
    :widths: 40 20 40

    * - Command
      - Roles
      - Description
    * - ``.rt stats``
      - DEVELOPER
      - Process CPU, memory and uptime.
    * - ``.rt eval`` / ``py`` / ``py3`` / ``python`` / ``exec``
      - DEVELOPER
      - Execute arbitrary Python in the bot's context.
    * - ``.rt bash`` / ``sh``
      - DEVELOPER
      - Execute a shell command on the host.

.. danger::

    ``.rt eval`` and ``.rt bash`` are unsandboxed remote code execution. They do
    nothing unless the bot was started with
    ``Raito(..., enable_dangerous_commands=True)``, and even then only the
    ``developer`` role can run them. Leave the flag off in production.

.. note::

    The eval context exposes helpers prefixed with ``_``: ``_msg``, ``_user``,
    ``_raito``, ``_bot``, ``_state`` and ``_command``.
