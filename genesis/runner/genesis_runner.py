import os
import yaml

from pathlib import Path
from loguru import logger

from config.config_service import ConfigService
from browser.browser_manager import BrowserManager
from engine.execution_context import ExecutionContext
from engine.provision_engine import ProvisionEngine
from core_logging.logger_config import configure_logger
from utils import trace
from utils.espera import mostrar_popup
from utils.versao_gen import set_versao


class GenesisRunner:
    """
    Orchestrates the full provisioning lifecycle.

    Responsibilities:
        - Load configuration
        - Load blueprint
        - Start browser
        - Create execution context
        - Execute provisioning engine
        - Ensure safe shutdown
        - Return exit code
    
    Contains NO domain logic.
    """

    def __init__(self, config_path: Path):
        self._config_path = config_path
        self._browser_manager: BrowserManager | None = None

    
    # --- Public API ---
    def run(self) -> int:
        """
        Executes full Genesis lifecycle.

        Returns:
            int: 0 on success, 1 on failure
        """
        try:
            configure_logger()
            logger.info("Iniciando Genesis.")


            trace_path = Path(__file__).resolve().parents[2] / "genesis" / "trace"
            trace.iniciar(trace_path)

            runtime_config = self._load_config()
            blueprint = self._load_blueprint(runtime_config)

            set_versao(runtime_config["versao"])

            self._browser_manager = BrowserManager()
            slow_mo = int(os.environ.get("ASI_SLOW_MO", 0))
            self._browser_manager.start(headless=False, slow_mo=slow_mo)

            context = ExecutionContext(
                browser_manager=self._browser_manager,
                runtime_config=runtime_config,
                blueprint=blueprint,
            )

            engine = ProvisionEngine(context)
            engine.execute()

            logger.success("Genesis finalizado com sucesso.")
            mostrar_popup("SUCESSO", "Genesis finalizado com sucesso.", 0x40)
            return 0
        
        except Exception:
            logger.exception("A execução do Genesis falhou.")
            mostrar_popup("FALHOU", "A execução do Genesis Falhou.",0x10)
            return 1

        finally:
            self._safe_shutdown()
    
    
    # --- Internal ---
    def _load_config(self) -> dict:
        config_service = ConfigService(self._config_path)
        runtime_config = config_service.get_runtime_config()

        logger.info("Configuração carregada com sucesso.")
        return runtime_config


    def _load_blueprint(self, runtime_config: dict) -> dict:
        arquivo_dados = runtime_config["arquivo_dados"]
        blueprint_path = Path(__file__).resolve().parents[2] / arquivo_dados

        if not blueprint_path.exists():
            raise FileNotFoundError(
                f"Blueprint file not found: {blueprint_path}"
            )
        
        with open(blueprint_path, "r", encoding="utf-8") as f:
            blueprint = yaml.safe_load(f) or {}
        
        client_id = runtime_config["cliente"]
        if not isinstance(blueprint, dict) or not blueprint:
            raise RuntimeError(f"Blueprint for client '{client_id}' is empty or invalid.")
        
        logger.info("Blueprint do cliente '{}' foi carregada com sucesso.", client_id)
        return blueprint
    

    def _safe_shutdown(self) -> None:
        if not self._browser_manager:
            return
        
        try:
            self._browser_manager.close()
            logger.info("Finalização do browser completa.")
        except Exception:
            # Never mask original exception
            logger.error("Erro durante encerramento do browser.")
