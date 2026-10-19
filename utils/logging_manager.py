from pathlib import Path
from datetime import datetime
from loguru import logger
from utils import logger_config, retencao

_run_dir: Path | None = None
_sink_id: int | None = None


def _sanitize_nodeid(nodeid: str) -> str:
    invalid_chars = '<>:"\\|?*'
    sanitized = nodeid.replace("/", "_").replace("::", "__")
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")
    return sanitized


def cleanup_old_runs(base_path: Path) -> None:
    """
    Remove pastas de log expiradas, conforme `configs/retencao.yaml`.

    Expected folder pattern: YYYY-MM-DD
    """
    retencao.varrer_por_data(
        base_path,
        retencao.FORMATO_DIARIO,
        retencao.dias("logs_dias"),
    )


def iniciar(base_path: Path):
    """
    Initialize logging for the test session.
    """
    global _run_dir

    base_path.mkdir(parents=True, exist_ok=True)
    cleanup_old_runs(base_path)

    today = datetime.now().strftime("%Y-%m-%d")
    _run_dir = base_path / today
    _run_dir.mkdir(parents=True, exist_ok=True)

    # Keep logging behavior centralized in logger_config.
    logger_config.configure_logger()


def iniciar_teste(nodeid: str):
    """
    Create log file for a test.
    """
    global _sink_id

    if not _run_dir:
        return

    # Defensive cleanup in case the previous test did not close its sink.
    finalizar_teste()

    safe_name = _sanitize_nodeid(nodeid)
    log_file = _run_dir / f"{safe_name}.txt"

    _sink_id = logger.add(
        log_file,
        level=logger_config.FILE_LEVEL,
        format=logger_config.FILE_FORMAT,
        enqueue=True,
    )


def finalizar_teste():
    global _sink_id

    if _sink_id is not None:
        logger.remove(_sink_id)
        _sink_id = None
