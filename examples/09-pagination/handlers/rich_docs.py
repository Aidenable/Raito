from aiogram import Bot, Router, filters
from aiogram.types import (
    CallbackQuery,
    InputRichBlockDetails,
    InputRichBlockDivider,
    InputRichBlockList,
    InputRichBlockListItem,
    InputRichBlockParagraph,
    InputRichBlockPreformatted,
    InputRichBlockSectionHeading,
    InputRichBlockTable,
    InputRichMessage,
    Message,
    RichBlockTableCell,
    RichTextBold,
    RichTextItalic,
)

from raito import Raito, rt
from raito.plugins.pagination import PaginationMode, RichPaginator

router = Router(name="rich_docs")

PAGES = {
    1: [
        InputRichBlockSectionHeading(text="Raito", size=1),
        InputRichBlockParagraph(
            text=[
                "A ",
                RichTextBold(text="type-safe"),
                " aiogram framework with ",
                RichTextItalic(text="batteries included"),
                ".",
            ]
        ),
        InputRichBlockList(
            items=[
                InputRichBlockListItem(blocks=[InputRichBlockParagraph(text="Scenes")]),
                InputRichBlockListItem(blocks=[InputRichBlockParagraph(text="Pagination")]),
                InputRichBlockListItem(blocks=[InputRichBlockParagraph(text="Roles")]),
            ]
        ),
    ],
    2: [
        InputRichBlockSectionHeading(text="Paginator modes", size=2),
        InputRichBlockTable(
            cells=[
                [
                    RichBlockTableCell(text="Mode", align="left", valign="middle", is_header=True),
                    RichBlockTableCell(
                        text="Content", align="left", valign="middle", is_header=True
                    ),
                ],
                [
                    RichBlockTableCell(text="text", align="left", valign="middle"),
                    RichBlockTableCell(text="plain text", align="left", valign="middle"),
                ],
                [
                    RichBlockTableCell(text="rich", align="left", valign="middle"),
                    RichBlockTableCell(text="blocks", align="left", valign="middle"),
                ],
            ]
        ),
        InputRichBlockDivider(),
    ],
    3: [
        InputRichBlockSectionHeading(text="Usage", size=2),
        InputRichBlockPreformatted(
            text="await paginator.answer(rich_message=...)",
            language="python",
        ),
        InputRichBlockDetails(
            summary="Why rich?",
            blocks=[
                InputRichBlockParagraph(
                    text="Tables, headings and collapsible sections — without hand-rolled HTML."
                )
            ],
        ),
    ],
}


@router.message(filters.Command("rich"))
async def start_rich(message: Message, raito: Raito, bot: Bot) -> None:
    if not message.from_user:
        return

    await raito.paginate(
        "rich_docs",
        chat_id=message.chat.id,
        bot=bot,
        from_user=message.from_user,
        mode=PaginationMode.RICH,
        total_pages=len(PAGES),
        limit=1,
    )


@rt.on_pagination(router, "rich_docs")
async def on_rich_pagination(query: CallbackQuery, paginator: RichPaginator, page: int) -> None:
    await paginator.answer(rich_message=InputRichMessage(blocks=PAGES[page]))
