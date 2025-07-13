from random import sample

from aiogram import Bot, Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from raito import rt
from raito.core.raito import Raito
from raito.plugins.pagination import InlinePaginator

router = Router(name="start")


@router.message(filters.CommandStart())
async def start(message: Message, raito: Raito, state: FSMContext, bot: Bot) -> None:
    if not message.from_user:
        return

    numbers = list(sample(range(100000), k=64))
    await state.update_data(numbers=numbers)

    LIMIT = 10
    total_pages = InlinePaginator.calc_total_pages(len(numbers), LIMIT)
    await raito.paginate(
        "emoji_list",
        chat_id=message.chat.id,
        bot=bot,
        from_user=message.from_user,
        total_pages=total_pages,
        limit=LIMIT,
    )
