The role model
==============

Raito's roles are deliberately simple. Understanding the model prevents
surprises — especially around who can grant what.

One role per user, no hierarchy
-------------------------------

Every user has **exactly one** stored role (or none). Roles are **flat**: there
is no ordering in which ``owner`` "contains" ``administrator``. A role used as a
filter passes only if the user's stored role equals it. That is why you write
``OWNER | ADMINISTRATOR | MODERATOR`` — you list every role that should pass,
because none implies another.

The ``|`` combinator is therefore an OR over roles, and it is the only
combinator you need: with one role per user, AND would never match.

Roles as filters
----------------

A built-in role like ``OWNER`` is a filter object. When aiogram evaluates it, it
asks the role manager whether the current user holds that role slug, using the
bot id and user id. Because Raito registers itself in the dispatcher context,
that lookup is available to every handler and filter through dependency
injection.

The same filters also carry metadata (the role's emoji and label) as flags, which
:meth:`~raito.Raito.register_commands` reads to scope the slash menu per user.

Where roles are stored
----------------------

You never construct a provider directly. Raito picks one from the FSM
``storage`` you passed:

- ``MemoryStorage`` → in-memory (lost on restart);
- ``JSONStorage`` → a JSON file;
- Redis storage → Redis;
- SQLite / PostgreSQL storage → a SQL table.

All providers implement the same ``IRoleProvider`` interface, so the rest of the
system is backend-agnostic. Memory and JSON are for development; Raito warns if
you run them with ``production=True``.

Developers are special
----------------------

User IDs passed as ``developers`` implicitly hold the ``developer`` role without
any backend entry. This is how you bootstrap access to yourself before any role
has been assigned.

The escalation caveat
---------------------

Assignment is flat, and this has a security consequence worth stating plainly:
any user who can manage roles (``developer``, ``owner`` or ``administrator``) can
grant **any** role to anyone else, including ``owner`` and ``developer``. The only
built-in guardrails are that you can't change your own role and that a
non-manager can't assign at all — but two administrators can promote each other.

Because ``developer`` can enable the ``.rt eval`` / ``.rt bash`` code-execution
tools (when the bot opts in with ``enable_dangerous_commands=True``), treat the
managing roles as trusted-operator level. If you need a stricter policy — a real
hierarchy, or "only owner may grant owner" — subclass
:class:`~raito.plugins.roles.RoleManager` and enforce it in ``assign_role``.
