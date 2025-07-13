from random import randint, sample

from aiogram import Bot, F, Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from raito import rt
from raito.core.raito import Raito
from raito.plugins.pagination import InlinePaginator

router = Router(name="remove")


@router.callback_query(F.data == "remove")
async def remove(query: CallbackQuery, raito: Raito, state: FSMContext, bot: Bot) -> None:
    await query.answer()
    if not isinstance(query.message, Message):
        return

    data = await state.get_data()
    numbers: list[int] = data.get("numbers", [])

    if numbers:
        numbers.pop(0)
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
