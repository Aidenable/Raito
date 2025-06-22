import logging
from datetime import datetime
from typing import Literal, cast

__all__ = (
    "ColoredFormatter",
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
    def format(self, record: logging.LogRecord) -> str:
        levelname = cast(LEVEL, record.levelname)

        background_color = LEVEL_BACKGROUND_COLORS.get(levelname, "")
        foreground_color = LEVEL_FOREGROUND_COLORS.get(levelname, "")

        now = datetime.fromtimestamp(record.created).strftime("%d.%m.%Y %H:%M:%S")

        left = f"{BRIGHT_BLACK}{now}{RESET} {WHITE}{record.name}{RESET}"
        tab = " " * (64 - len(left))

        tag = f"{background_color} {levelname[0]} {RESET}"
        message = f"{foreground_color}{record.getMessage()}{RESET}"

        return f"{left}{tab} {tag} {message}"


core = logging.getLogger("raito.core")
routers = logging.getLogger("raito.core.routers")

middlewares = logging.getLogger("raito.middlewares")
plugins = logging.getLogger("raito.plugins")
roles = logging.getLogger("raito.plugins.roles")

log = logging.getLogger()
