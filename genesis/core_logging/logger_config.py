import json

from loguru import logger


def configure_logger(extra_sink=None) -> None:
    """
    Configure centralized logging for Genesis.

    This function must be called once at application startup (main.py).
    """

    # Remove default logger to avoid duplicate handlers
    logger.remove()

    # stdout sink (primary)
    logger.add(
        json_sink,
        backtrace=True,
        diagnose=True
    )

    if extra_sink is not None:
        logger.add(
            extra_sink,
            level="DEBUG",
            enqueue=True,
        )


def json_sink(message):
    record = message.record
    
    exception = ""
    if record["exception"]:
        import traceback
        exception = "".join(traceback.format_exception(*record["exception"]))

    log = {
        "level": record["level"].name,
        "message": record["message"],
        "time": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "exception": exception,
    }

    print(json.dumps(log), flush=True)
