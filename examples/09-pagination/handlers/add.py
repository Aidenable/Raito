from random import randint

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from raito import Raito
from raito.plugins.pagination import InlinePaginator

router = Router(name="add")


@router.callback_query(F.data == "add")
async def add(query: CallbackQuery, raito: Raito, state: FSMContext, bot: Bot) -> None:
    await query.answer()
    if not isinstance(query.message, Message):
        return

    data = await state.get_data()
    numbers: list[int] = data.get("numbers", [])

    numbers.insert(0, randint(1, 100000))
    await state.update_data(numbers=numbers)

    LIMIT = 10
    total_pages = InlinePaginator.calc_total_pages(len(numbers), LIMIT)
    await raito.paginate(
        "emoji_list",
        chat_id=query.message.chat.id,
        bot=bot,
        from_user=query.from_user,
        existing_message=query.message,
        total_pages=total_pages,
        limit=LIMIT,
    )
