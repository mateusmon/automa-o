from loguru import logger

from engine.execution_context import ExecutionContext
from routines.link_user import run as run_link_user
from routines.teste_user import run as run_teste_user


class ProvisionEngine:
    """
    Domain orchestrator for Genesis provisioning.

    Responsibilities:
        - Execute routines in explicit order
        - Enforce session boundary between user roles
        - Fail fast on any inconsistency
    
    Contains NO:
        - Playwright lifecycle control
        - Flow logic
        - Config loading
        - Blueprint parsing
    """

    def __init__(self, context: ExecutionContext) -> None:
        self._context = context
    
    
    # --- Public API ---
    def execute(self) -> None:
        """
        Executes full provisioning sequence.

        Raises:
            Any exception raised by routines (fail-fast policy).
        """
        logger.info("Iniciando execução de provisão de dados.")

        # --- LINK USER ROUTINE ---
        self._run_link_user()

        # --- SESSION RESET (role boundary) ---
        self._reset_session()

        # --- TEST USER ROUTINE ---
        self._run_teste_user()

        logger.success("Provisão de dados completada com sucesso.")
    

    # --- Internal ---
    def _run_link_user(self) -> None:
        logger.info("Executando a rotina do usuário Link.")
        run_link_user(self._context)
    

    def _run_teste_user(self) -> None:
        logger.info("Executando a rotina do usuário Teste.")
        run_teste_user(self._context)
    

    def _reset_session(self) -> None:
        logger.info("Redefinindo a sessão do usuário da Link para o usuário Teste.")
        self._context.browser_manager.reset_context()
