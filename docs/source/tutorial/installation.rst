Installation
============

Raito requires **Python 3.10+** and **aiogram 3.20+**.

Install from PyPI
-----------------

.. code-block:: bash

    pip install -U raito

Or with your tool of choice:

.. code-block:: bash

    uv add raito
    poetry add raito

Optional extras
---------------

Raito's persistent storages and role backends are optional. Install only what
you need:

============================  ===================================================
Extra                         Enables
============================  ===================================================
``raito[sqlite]``             SQLite FSM storage and role provider (SQLAlchemy + aiosqlite)
``raito[postgresql]``         PostgreSQL FSM storage and role provider (SQLAlchemy + asyncpg)
``raito[redis]``              Redis role provider
============================  ===================================================

.. code-block:: bash

    pip install -U "raito[sqlite]"

Without an extra, Raito falls back to in-memory / JSON storage, which is perfect
for development but **not recommended for production** (Raito will warn you at
startup).

Verify the install
------------------

.. code-block:: bash

    python -c "import raito; print(raito.Raito)"

You should see ``<class 'raito.core.raito.Raito'>``. Continue to
:doc:`your-first-bot`.
