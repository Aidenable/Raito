🎭 Roles
=============================

Raito provides a powerful role-based access control system with:

- Named roles (with emoji, label, description)
- Role filters and constraints (``|`` composition supported)
- Telegram-based role management via ``.rt`` commands
- Auto-synced slash commands by user role
- Pluggable storage backends (memory, JSON, Redis, SQL)

------

Usage
~~~~~~~~~~~~~~~

Raito ships with built-in roles:

.. code-block:: python

   from raito.plugins.roles.roles import ADMINISTRATOR, DEVELOPER, GUEST, SUPPORT, ...

Each role acts as a filter:

.. code-block:: python

   @router.message(ADMINISTRATOR)
   async def only_admins(message: Message): ...

You can combine roles with ``|``:

.. code-block:: python

   @router.message(DEVELOPER | OWNER | ADMINISTRATOR)
   async def internal(message: Message): ...

-----

Managing Roles
~~~~~~~~~~~~~~~

Use Telegram commands to manage roles:

.. code-block:: text

   .rt assign   → choose role from buttons
   .rt revoke   → enter user ID to revoke role
   .rt staff    → list users with roles

To manage roles, you must already have one of the following:

- `developer`
- `owner`
- `administrator`

.. tip::
    You can override ``RoleManager`` to implement custom permission rules.

-----

Role-based Slash Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Call this to register commands:

.. code-block:: python

   await raito.register_commands(bot)

What it does:

- Collects all handlers
- Detects required roles (via filters)
- Sets slash commands per user, based on their role
- Uses ``emoji`` and ``description`` for clarity

Each user sees **only** the commands they’re allowed to use.

-----

Storage Backends
~~~~~~~~~~~~~~~~~

You can persist role data using any backend:

.. code-block:: python

   # from raito.plugins.roles.providers import MemoryRoleProvider
   from raito.plugins.roles.providers import get_redis_provider
   # from raito.plugins.roles.providers import get_postgresql_provider
   # from raito.plugins.roles.providers import get_sqlite_provider


   RedisRoleProvider = get_redis_provider()
   raito = Raito(..., role_provider=RedisRoleProvider(...))

All providers follow a common ``IRoleProvider`` interface.

------

RoleManager API
~~~~~~~~~~~~~~~~~

Use ``raito.role_manager`` to work with roles manually:

- ``assign_role(bot_id, from_id, to_id, role)``
- ``revoke_role(bot_id, from_id, to_id)``
- ``get_users(bot_id, role)``
- ``has_role(...)``, ``has_any_roles(...)``

Access control is enforced on ``assign`` / ``revoke``:

- Only trusted roles can assign
- You can't assign or revoke your own role

-----

Custom Roles
~~~~~~~~~~~~

Need your own role? Just define one:

.. code-block:: python

   from raito.plugins.roles.constraint import RoleConstraint
   from raito.plugins.roles.filter import RoleFilter

   MODERATOR = RoleConstraint(
       RoleFilter(
           slug="dude",
           name="Dude",
           description="Just a dude",
           emoji="😎",
       )
   )

To make your role show up in ``.rt staff``, add it to ``RoleManager.available_roles``.

------

Tips
~~~~~~

- Use ``@rt.description(...)`` to describe restricted commands
- Always re-check roles in long-running flows (e.g. FSM)
- SQL or Redis backends are recommended for production
