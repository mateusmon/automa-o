# Rota A do pipeline de logs: Loguru → GuiLogSink → app.log → queue → LogPanel
# Cobre todo o código Python da aplicação (app.py, genesis_runner.py, etc.)
#
# Rota B (paralela): TestRunner lê o stdout do pytest linha a linha e chama
# app.log() diretamente, sem passar pelo Loguru. Qualquer filtro aplicado aqui
# NÃO afeta o output do pytest — as duas rotas precisam ser tratadas separadamente.
class GuiLogSink:
    """
    Loguru sink that redirects logs to the GUI safely.
    """

    def __init__(self, app):
        self.app = app

    def write(self, message):
        """
        Called automatically by Loguru.
        """
        record = message.record

        level = record["level"].name
        text = record["message"]

        # Map Loguru levels → GUI tags
        level_map = {
            "TRACE": "DEBUG",
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "SUCCESS": "SUCCESS",
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "ERROR",
        }

        gui_level = level_map.get(level, "INFO")

        self.app.log(text, gui_level)
