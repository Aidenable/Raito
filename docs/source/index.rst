.. Raito documentation master file, created by sphinx-quickstart

That's Raito!
=============

*REPL, hot-reload, keyboards, pagination, and internal dev tools — all in one.*

Highlights
----------

* **🔥 Hot Reload** — automatic router loading and file watching for instant development cycles
* **🎭 Role System** — ``@raito.roles`` with pre-configured roles (admin, mod, support, etc) and selector UI
* **📚 Pagination** — easy pagination over text and media using inline buttons
* **💬 FSM Toolkit** — interactive confirmations, questionnaires, and mockable message flow
* **🚀 CLI Generator** — ``$ raito init`` creates a ready-to-use bot template in seconds
* **🛠️ Command Registration** — automatic setup of bot commands with descriptions for each
* **🛡️ Rate Limiting** — apply global or per-command throttling via decorators or middleware
* **💾 Database Storages** — optional SQL support
* **🧪 REPL** — execute async Python in context (``_msg``, ``_user``, ``_raito``)
* **🔍 Params Parser** — extracts and validates command arguments
* **📊 Metrics** — inspect memory usage, uptime, and caching stats
* **📃 Logging** — view and filter runtime logs without leaving Telegram
* **🧰 Debug Utils** — run shell commands, monitor jobs, inspect command states, and more

-------------------

Get started, explore the API, or dive into individual modules:

Getting Started 📚
~~~~~~~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 1

   usage/installation
   usage/quick-start

Plugins 🔌
~~~~~~~~~~~
.. toctree::
   :maxdepth: 1

   raito.plugins.pagination
   raito.plugins.roles

Core & Internals ⚙️
~~~~~~~~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 1

   raito.core
   raito.utils

References 🔍
~~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 1

   changelog

Indices & Tables 🗂️
~~~~~~~~~~~~~~~~~~
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
