from __future__ import annotations

import time
from typing import TYPE_CHECKING

import psutil
from aiogram import Router, html

from raito.plugins.commands import description, hidden
from raito.plugins.roles.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.types import Message

router = Router(name="raito.system.stats")


def get_process_stats():
    proc = psutil.Process()

    with proc.oneshot():
        mem_info = proc.memory_info()
        cpu_percent = proc.cpu_percent(interval=0.1)
        create_time = proc.create_time()

    return {
        "uptime_sec": time.time() - create_time,
        "memory": {
            "rss_mb": mem_info.rss / 1024**2,
            "vms_mb": mem_info.vms / 1024**2,
        },
        "cpu_percent": cpu_percent,
    }


def strf_seconds(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return (
        (f"{days}d " if days else "")
        + (f"{hours}h " if hours else "")
        + (f"{minutes}m " if minutes else "")
        + (f"{seconds}s" if seconds else "")
    )


@router.message(RaitoCommand("stats"), DEVELOPER)
@description("Show process stats")
@hidden
async def stats(message: Message):
    stats = get_process_stats()

    text = (
        html.bold("Process stats")
        + "\n"
        + "CPU: "
        + "{:.2f}".format(stats["cpu_percent"])
        + "%\n"
        + "RAM: "
        + "{:.2f}".format(stats["memory"]["rss_mb"])
        + "Mb\n"
        + "Uptime: "
        + strf_seconds(int(stats["uptime_sec"]))
    )
    await message.answer(text=text, parse_mode="HTML")
