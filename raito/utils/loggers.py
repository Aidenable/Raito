import logging
import shutil
from datetime import datetime
from typing import Literal, cast

from typing_extensions import override

__all__ = (
    "ColoredFormatter",
    "MuteLoggersFilter",
    "core",
    "log",
    "middlewares",
    "plugins",
    "roles",
)

LEVEL = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

WHITE = "\033[37m"
BRIGHT_BLACK = "\033[90m"
RESET = "\033[0m"

LEVEL_BACKGROUND_COLORS: dict[LEVEL, str] = {
    "DEBUG": "\033[42m",
    "INFO": "\033[104m",
    "WARNING": "\033[103m",
    "ERROR": "\033[101m",
    "CRITICAL": "\033[41m",
}

LEVEL_FOREGROUND_COLORS: dict[LEVEL, str] = {
    "DEBUG": "\033[32m",
    "INFO": RESET,
    "WARNING": RESET,
    "ERROR": RESET,
    "CRITICAL": "\033[31m",
}


class ColoredFormatter(logging.Formatter):
    @property
    def terminal_width(self) -> int:
        try:
            return shutil.get_terminal_size().columns
        except OSError:
            return 80

    @override
    def format(self, record: logging.LogRecord) -> str:
        levelname = cast(LEVEL, record.levelname)

        meta = self.get_meta(record)
        message = self.get_message(record, levelname)

        if not meta:
            return message
        return f"{meta} {message}"

    def get_meta(self, record: logging.LogRecord) -> str:
        dt = datetime.fromtimestamp(record.created)
        date = dt.strftime("%d.%m.%Y")
        time = dt.strftime("%H:%M:%S")
        now = date + " " + time

        if self.terminal_width >= 140:
            info = f"{BRIGHT_BLACK}{now}{RESET} {WHITE}{record.name}{RESET}"
            tabs = " " * (64 - len(info))
            return info + tabs
        elif self.terminal_width >= 100:
            return f"{BRIGHT_BLACK}{now}{RESET}"
        elif self.terminal_width >= 70:
            return f"{BRIGHT_BLACK}{time}{RESET}"
        else:
            return ""

    def get_message(self, record: logging.LogRecord, levelname: LEVEL) -> str:
        background = LEVEL_BACKGROUND_COLORS.get(levelname, "")
        tag = f"{background} {levelname[0]} {RESET}"

        foreground = LEVEL_FOREGROUND_COLORS.get(levelname, "")
        message = f"{foreground}{record.getMessage()}{RESET}"
        return f"{tag} {message}"


class MuteLoggersFilter(logging.Filter):
    def __init__(self, *names: str) -> None:
        self.names = set(names)
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name not in self.names


core = logging.getLogger("raito.core")
routers = logging.getLogger("raito.core.routers")
commands = logging.getLogger("raito.core.commands")

middlewares = logging.getLogger("raito.middlewares")
plugins = logging.getLogger("raito.plugins")
roles = logging.getLogger("raito.plugins.roles")

utils = logging.getLogger("raito.utils")
storages = logging.getLogger("raito.utils.storages")

log = logging.getLogger()
