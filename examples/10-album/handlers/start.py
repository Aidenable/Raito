from random import sample

from aiogram import Bot, F, Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InputMediaPhoto, InputMediaVideo, Message

from raito.core.raito import Raito
from raito.plugins.pagination import InlinePaginator

router = Router(name="start")


class Form(StatesGroup):
    media = State()


@router.message(filters.CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await message.answer("Send me a photo, a video — or both!")
    await state.set_state(Form.media)


@router.message(Form.media, ~F.media_group_id, F.photo | F.video)
async def single_media(message: Message) -> None:
    if message.photo:
        await message.answer_photo(caption="Nice shot!", photo=message.photo[-1].file_id)
    if message.video:
        await message.answer_video(caption="Cool video!", video=message.video.file_id)


@router.message(Form.media, F.media_group_id)
async def media_group(message: Message, album: list[Message] = []) -> None:
    if not album:
        await message.answer("Hmm, looks like the album is empty...")
        return

    caption = "Awesome album!"
    elements = []
    for element in album:
        if element.photo:
            input = InputMediaPhoto(media=element.photo[-1].file_id, caption=caption)
        elif element.video:
            input = InputMediaVideo(media=element.video.file_id, caption=caption)
        else:
            continue
        elements.append(input)

    await message.answer_media_group(media=elements)
