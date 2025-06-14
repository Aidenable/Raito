from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import Message

from raito.utils.ascii import ascii_tree
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from raito.core.raito import Raito

router = Router(name="raito.management.list")


@router.message(RaitoCommand("list"))
async def list_routers(message: Message, raito: "Raito") -> None:
    await message.answer(ascii_tree(list(raito.manager.loaders.keys())))
