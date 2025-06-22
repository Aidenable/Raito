<div align="center">
    <h1 id="header" align="center">🔦 Raito</h1>
    <p align="center">REPL, hot-reload, keyboards, pagination, and internal dev tools — all in one. That's Raito.</p>
</div>

<div align="center">
<img alt="GitHub License" src="https://img.shields.io/github/license/Aidenable/Raito?style=for-the-badge&labelColor=252622&link=https%3A%2F%2Fgithub.com%2FAidenable%2FRaito%2Fblob%2Fmain%2FLICENSE">
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Aidenable/Raito?style=for-the-badge&labelColor=262422&color=F59937">
<img alt="PyPI - Version" src="https://img.shields.io/pypi/v/raito?style=for-the-badge&labelColor=222226&color=3760F5&link=https%3A%2F%2Fpypi.org%2Fproject%2Fraito%2F">
</div>

<div align="center">
<img alt="uv" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fastral-sh%2Fuv%2Fmain%2Fassets%2Fbadge%2Fv0.json&style=flat-square&labelColor=232226&color=6341AC&link=https%3A%2F%2Fastral.sh%2Fuv">
<img alt="Ruff" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fastral-sh%2Fruff%2Fmain%2Fassets%2Fbadge%2Fv2.json&style=flat-square&labelColor=232226&color=6341AC&link=https%3A%2F%2Fastral.sh%2Fruff">
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/raito?style=flat-square&labelColor=222426&color=19A4F3">
<img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/Aidenable/Raito/test.yml?style=flat-square&labelColor=232622">
</div>

---

## Highlights

- 🔥 **Hot Reload** — automatic router loading and file watching for instant development cycles
- 🎭 **Role System** — `@raito.roles` with pre-configured roles (admin, mod, support, etc) and selector UI
- 📚 **Pagination** — easy pagination over text and media using inline buttons
- 💬 **FSM Toolkit** — interactive confirmations, questionnaires, and mockable message flow
- 🚀 **CLI Generator** — `$ raito init` creates a ready-to-use bot template in seconds
- 🛠️ **Command Registration** — automatic setup of bot commands with descriptions for each
- 🛡️ **Rate Limiting** — apply global or per-command throttling via decorators or middleware
- 💾 **Database Storages** — optional SQL support
- 🧪 **REPL** — execute async Python in context (`_msg`, `_user`, `_raito`)
- 🔍 **Params Parser** — extracts and validates command arguments
- 📊 **Metrics** — inspect memory usage, uptime, and caching stats
- 📃 **Logging** — view and filter runtime logs without leaving Telegram
- 🧰 **Debug Utils** — run shell commands, monitor jobs, inspect command states, and more


## Installation

```bash
pip install -U raito
```


## Quick Start

```python
import asyncio

from aiogram import Bot, Dispatcher
from raito import Raito


async def main() -> None:
    bot = Bot(token="TOKEN")
    dispatcher = Dispatcher()
    raito = Raito(dispatcher, "src/handlers")

    await raito.setup()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## Why Raito?

Raito speeds up your bot development by removing the boring parts — no more boilerplate, no more manual restarts, no more duplicated code across projects. \
Everything that used to slow you down is already solved.


## Showcases

#### 📦 Handling Commands

You can control access to commands using `@rt.roles`

The `@rt.description` decorator adds a description to each command — they will show up in the slash menu automatically.

For commands like `/ban 1234`, use `@rt.params` to extract and validate the arguments.

```python
@router.message(filters.Command("ban"))
@rt.roles(rt.Role.OWNER, rt.Role.ADMINISTRATOR, rt.Role.MODERATOR)
@rt.description("Ban a user")
@rt.params(user_id=int)
async def ban(message: types.Message, params: rt.Params, bot: Bot):
    if not params.user_id:
        await message.answer("Please provide a user ID.")
        return

    await bot.ban_chat_member(chat_id=message.chat.id, user_id=params.user_id)
    await message.answer(text="✅ User banned successfully!")
```

---

#### 🔥 Hot-Reload & Router Management

Whenever you change a file with handlers, Raito automatically reloads it without restarting the bot.

You can also manage your routers manually using the `.rt load`, `.rt unload`, `.rt reload`, or `.rt routers` commands in the bot.

<video width="600" autoplay muted loop controls align="left">
  <source src=".github/assets/hot-reload.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

---

#### 🎭 Roles

Use built-in roles to set different access levels for team members.

<p align="left">
  <img src=".github/assets/roles.png" alt="Roles" width="600">
</p>


## Contributing

Have an idea, found a bug, or want to improve something? \
Contributions are welcome! Feel free to open an issue or submit a pull request.


## Security

If you discover a security vulnerability, please report it responsibly. \
You can open a private GitHub issue or contact the maintainer directly.

There’s no bounty program — this is a solo open source project. \
Use in production at your own risk.

> For full details, check out the [Security Policy](SECURITY.md).


## Questions?

Open an issue or start a discussion in the GitHub Discussions tab. \
You can also ping [@Aidenable](https://github.com/Aidenable) for feedback or ideas.

[![GO TOP](https://img.shields.io/badge/GO%20TOP-black?style=for-the-badge)](#header)
