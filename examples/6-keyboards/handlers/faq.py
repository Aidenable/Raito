from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito import rt

router = Router(name="faq")


@rt.keyboard.dynamic()
def faq_markup(builder: InlineKeyboardBuilder, tos_url: str, privacy_url: str) -> None:
    builder.button(text="Terms of Service", url=tos_url)
    builder.button(text="Privacy", url=privacy_url)


@router.message(F.text == "📄 FAQ")
async def faq(message: Message) -> None:
    await message.answer(
        "🏀 Welcome to the <b>World Telegram Basketball Championship!</b>\n"
        "\n"
        "<i>• What’s the prize pool?</i>\n"
        "Money isn’t the main thing.\n"
        "\n"
        "<i>• How many people are participating?</i>\n"
        "Roughly between 2 and 200,000.\n"
        "\n"
        "<i>• Who sponsors the championship?</i>\n"
        "Our main sponsors are: RedBull, Nike, Raito Sports, Visa.",
        reply_markup=faq_markup(tos_url="https://example.com", privacy_url="https://example.com"),
    )
