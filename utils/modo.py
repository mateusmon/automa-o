from loguru import logger

_headless: bool = False


def set_headless(value: bool) -> None:
    global _headless
    _headless = value
    logger.debug("Modo headless: {}", value)


def is_headless() -> bool:
    return _headless
