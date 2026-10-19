import sys

from loguru import logger
from pathlib import Path

from core_logging.logger_config import configure_logger
from runner.genesis_runner import GenesisRunner


def main() -> int:
    configure_logger()

    logger.info("Iniciando Genesis para criação de massa de dados.")

    runner = GenesisRunner(
        config_path=Path(__file__).resolve().parent.parent / "configs" / "configs.yaml"
    )
    
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
