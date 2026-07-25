🎭 Roles
========

Raito ships a role-based access control system:

- named roles (each with a slug, label, emoji and description);
- roles double as aiogram filters, composable with ``|``;
- in-chat management via ``.rt`` commands;
- slash commands auto-scoped per user by role;
- pluggable backends (memory, JSON, Redis, SQL).

Gate a handler by role
----------------------

Import the built-in roles from ``rt`` (or ``raito.plugins.roles``) and use them
as filters. A role passes only if the user currently holds it:

.. code-block:: python

    from aiogram import Router, filters, types
    from raito.rt import OWNER, ADMINISTRATOR, MODERATOR

    router = Router(name="moderation")


    @router.message(filters.Command("ban"), OWNER | ADMINISTRATOR | MODERATOR)
    async def ban(message: types.Message) -> None:
        ...

``A | B`` means "any of these roles". This is the only combinator — a user holds
exactly one role, so ``|`` (OR) is what you need. There is no role hierarchy:
``OWNER`` does not implicitly satisfy an ``ADMINISTRATOR`` filter, so list every
role that should pass.

Grant yourself access
---------------------

Pass trusted user IDs as ``developers``. They implicitly hold the ``developer``
role without touching the backend:

.. code-block:: python

    raito = Raito(dispatcher, "handlers", developers=[123456789])

Choose a backend
----------------

The role backend is derived from the FSM ``storage`` you give Raito — you do not
wire a provider by hand:

===============================================  ==============================
``storage=``                                     Role backend
===============================================  ==============================
``MemoryStorage`` (default)                      in-memory (lost on restart)
:class:`~raito.utils.storages.json.JSONStorage`  JSON file
``RedisStorage``                                 Redis
SQLite / PostgreSQL storage                      SQL table
===============================================  ==============================

.. code-block:: python

    from raito import Raito
    from raito.utils.storages import get_sqlite_storage

    SQLiteStorage = get_sqlite_storage()
    storage = SQLiteStorage("sqlite+aiosqlite:///bot.db")

    raito = Raito(dispatcher, "handlers", storage=storage)

Memory and JSON are fine for development; Raito warns at startup if you use them
with ``production=True``. Use Redis or SQL in production.

Manage roles from the chat
--------------------------

A user who already holds a managing role can assign roles to others without
leaving Telegram:

.. code-block:: text

    .rt roles    → pick a role, then send a user ID
    .rt revoke   → send a user ID to remove their role
    .rt staff    → tree of all users grouped by role

Managing roles requires ``developer``, ``owner`` or ``administrator``.

.. warning::

    Role assignment is **flat**: any managing role can grant *any* role,
    including ``owner`` and ``developer``. An ``administrator`` can therefore
    escalate another user (and, via a second admin, themselves) to
    ``developer``. Grant the managing roles only to people you trust with that.

Manage roles from code
----------------------

``raito.role_manager`` exposes the same operations:

.. code-block:: python

    from aiogram import Router, filters, types
    from raito import Raito, rt
    from raito.rt import ADMINISTRATOR, DEVELOPER, OWNER

    router = Router(name="tester")


    @router.message(filters.Command("give_tester"), DEVELOPER | OWNER | ADMINISTRATOR)
    @rt.params(user_id=int)
    async def give_tester(message: types.Message, raito: Raito, user_id: int) -> None:
        await raito.role_manager.assign_role(
            message.bot.id, message.from_user.id, user_id, "tester"
        )
        await message.answer(f"User <code>{user_id}</code> is now a tester!", parse_mode="HTML")

Key methods: ``assign_role(bot_id, initiator_id, target_id, slug)``,
``revoke_role(bot_id, initiator_id, target_id)``, ``get_role(bot_id, user_id)``,
``has_role(...)``, ``has_any_roles(...)``, ``get_users(bot_id, slug)``. ``assign``
and ``revoke`` enforce that the initiator can manage roles and is not changing
their own — a :class:`PermissionError` is raised otherwise.

Auto-scoped slash commands
--------------------------

Call :meth:`~raito.Raito.register_commands` (usually from a
:doc:`lifespan <lifespan>` handler) to publish the slash menu. Raito reads each
handler's role filter and its :func:`~raito.rt.description`, then sets the menu
per user so everyone sees only the commands they may run:

.. code-block:: python

    await raito.register_commands(bot)

Built-in roles
--------------

.. list-table::
    :header-rows: 1
    :widths: 22 14 64

    * - Role
      - Slug
      - Description
    * - 🖥️ Developer
      - developer
      - Full access, including debug tools and unsafe operations.
    * - 👑 Owner
      - owner
      - Top-level administrator; manages administrators and global settings.
    * - 💼 Administrator
      - administrator
      - Manages users, moderates content, configures most settings.
    * - 🛡️ Moderator
      - moderator
      - Moderates activity, issues warnings, enforces rules.
    * - 📊 Manager
      - manager
      - Oversees non-technical operations (campaigns, tasks, content).
    * - ❤️ Sponsor
      - sponsor
      - Supporter of the project; usually no admin privileges.
    * - 👤 Guest
      - guest
      - Temporary access to specific features; typically invited users.
    * - 💬 Support
      - support
      - Handles user support and onboarding.
    * - 🧪 Tester
      - tester
      - Tests new features; may access experimental tools.

Custom roles
------------

Define a role by wrapping a :class:`~raito.plugins.roles.filter.RoleFilter` in a
:class:`~raito.plugins.roles.constraint.RoleConstraint`:

.. code-block:: python

    from raito.plugins.roles.constraint import RoleConstraint
    from raito.plugins.roles.filter import RoleFilter

    DUDE = RoleConstraint(
        RoleFilter(slug="dude", name="Dude", description="Just a dude", emoji="😎")
    )

Use ``DUDE`` as a filter like any built-in role. To make it manageable and
visible in ``.rt staff``, subclass :class:`~raito.plugins.roles.RoleManager`
(overriding ``available_roles`` / ``get_role_data`` and, if needed, the
permission checks) and pass it via
``configuration=RaitoConfiguration(role_manager=...)``.

.. tip::

    In long-running FSM flows, re-check the role at each step — a user's role can
    change between messages.
