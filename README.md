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
<img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/Aidenable/Raito/ci.yml?style=flat-square&labelColor=232622">
</div>

---

## Highlights

- 🔥 **Hot Reload** — automatic router loading and file watching for instant development cycles
- 🎭 **Role System** — pre-configured roles (owner, support, tester, etc) and selector UI
- 📚 **Pagination** — easy pagination over text and media using inline buttons
- 💬 **FSM Toolkit** — interactive confirmations, questionnaires, and mockable message flow
- 🚀 **CLI Generator** — `$ raito init` creates a ready-to-use bot template in seconds
- ⌨️ **Keyboard Factory** — static and dynamic generation
- 🛠️ **Command Registration** — automatic setup of bot commands with descriptions for each
- 🖼️ **Album Support** — groups media albums and passes them to handlers
- 🛡️ **Rate Limiting** — apply global or per-command throttling via decorators or middleware
- 💾 **Database Storages** — optional JSON & SQL support
- 🧪 **REPL** — execute async Python in context (`_msg`, `_user`, `_raito`)
- 🔍 **Params Parser** — extracts and validates command arguments
- ✏️ **Logging Formatter** — beautiful, readable logs out of the box
- 📊 **Metrics** — inspect memory usage, uptime, and caching stats


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

Limit command usage with `@rt.limiter` and control the rate by mode.

```python
@router.message(filters.Command("ban"), OWNER | ADMINISTRATOR | MODERATOR)
@rt.description("Ban a user")
@rt.limiter(300, mode="chat")
@rt.params(user_id=int)
async def ban(message: types.Message, user_id: int, bot: Bot):
    await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
    await message.answer(text="✅ User banned successfully!")
```

---

#### 🔥 Hot-Reload & Router Management

Whenever you change a file with handlers, Raito automatically reloads it without restarting the bot.

You can also manage your routers manually using the `.rt load`, `.rt unload`, `.rt reload`, or `.rt routers` commands in the bot.

https://github.com/user-attachments/assets/c7ecfb7e-b709-4f92-9de3-efc4982cc926

---

#### 🎭 Roles

Use built-in roles to set different access levels for team members.

<p align="left">
  <img src=".github/assets/roles.png" alt="Roles" width="600">
</p>

---

#### 📚 Pagination

The simplest, most native and most effective pagination. Unlike many other libraries, it **does not use internal storage**. \
It is very user-friendly and fully customizable.

```python
@router.message(filters.Command("pagination"))
async def pagination(message: Message, raito: Raito, bot: Bot):
    if not message.from_user:
        return

    await raito.paginate(
        "button_list",
        chat_id=message.chat.id,
        bot=bot,
        from_user=message.from_user,
        limit=5,
    )


# mock data
BUTTONS = [
    InlineKeyboardButton(text=f"Button #{i}", callback_data=f"button:{i}")
    for i in range(10000)
]

@rt.on_pagination(router, "button_list")
async def on_pagination(query: CallbackQuery, paginator: InlinePaginator, offset: int, limit: int):
    content = BUTTONS[offset : offset + limit]
    await paginator.answer(text="Here is your buttons:", buttons=content)
```

---

#### ⌨️ Keyboards

Sometimes you want quick layouts. Sometimes — full control. You get both.

##### Static (layout-based)
```python
@rt.keyboard.static(inline=True)
def information():
    return [
        ("📄 Terms of Service", "tos"),
        [("ℹ️ About", "about"), ("⚙️ Website", "web")],
    ]
```

##### Dynamic (builder-based)
```python
@rt.keyboard.dynamic(1, 2, adjust=True, inline=False)
def start_menu(builder: ReplyKeyboardBuilder, app_url: str):
    builder.button(text="📱 Open App", web_app=WebAppInfo(url=app_url))
    builder.button(text="💬 Support")
    builder.button(text="📢 Channel")
```

---

#### 🍃 Lifespan

Define startup and shutdown logic in one place.

```python
@rt.lifespan(router)
async def lifespan(bot: Bot):
    user = await bot.get_me()
    rt.debug("🚀 Bot [%s] is starting...", user.full_name)

    yield

    rt.debug("👋🏻 Bye!")
```

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

![Alt](https://repobeats.axiom.co/api/embed/6ba46ed9f14186eb039044610072e123c0afeb08.svg "Repobeats analytics image")

[![GO TOP](https://img.shields.io/badge/GO%20TOP-black?style=for-the-badge)](#header)
