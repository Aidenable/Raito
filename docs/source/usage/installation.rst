🛠️ Installation
================

Raito supports installation via all popular Python package managers.

.. code-block:: bash

   pip install raito

or, if you use ``uv``:

.. code-block:: bash

   uv add raito

or with ``poetry``:

.. code-block:: bash

   poetry add raito

or with ``pipenv``:

.. code-block:: bash

   pipenv install raito

Optional Extras
~~~~~~~~~~~~~~~

To enable optional features like SQLite/PostgreSQL support, and redis cluster — install with `extras`:

.. code-block:: bash

   pip install 'raito[sqlite]'
   pip install 'raito[postgres]'
   pip install 'raito[redis]'

Multiple extras can be combined:

.. code-block:: bash

   pip install 'raito[sqlite,dev]'

Available Extras
~~~~~~~~~~~~~~~~

- ``sqlite`` — adds SQLite support via `aiosqlite` and `sqlalchemy`.
- ``postgres`` — adds PostgreSQL support via `asyncpg` and `sqlalchemy`.
- ``redis`` — adds Redis support via `redis`.

Development Setup
~~~~~~~~~~~~~~~~~

To install all extras and setup a dev environment:

.. code-block:: bash

   git clone https://github.com/Aidenable/Raito
   cd Raito
   uv pip install -e '.[dev,redis,sqlite,postgres]'
