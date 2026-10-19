import sys
from loguru import logger

CONSOLE_LEVEL = "DEBUG"
FILE_LEVEL = "DEBUG"

CONSOLE_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level}</level> | "
    "{message}"
)

FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "{level} | "
    "{message} | "
    "{name}:{function}:{line}"
)

_console_sink_id: int | None = None


def configure_logger():
    """
    Configure base logger behavior.

    This module answers: "how do we log?" (formats, levels, sinks).
    Storage location/retention are handled by logging_manager.
    """
    global _console_sink_id

    logger.remove()
    _console_sink_id = logger.add(
        sys.stdout,
        level=CONSOLE_LEVEL,
        format=CONSOLE_FORMAT,
        enqueue=True,
        filter=lambda record: not record["extra"].get("apenas_arquivo", False)
    )
    return logger
