import json
import subprocess
import threading
import sys
import os

from pathlib import Path
from loguru import logger


class GenesisRunner:
    def __init__(self, app):
        self.app = app
        self.process = None
        self.is_running = False
    
    def run(self, slow_mo: int = 0):
        if self.is_running:
            logger.warning("Genesis já está em execução.")
            return

        self.is_running = True
        self.app.after(0, lambda: self.app._set_ui_running_state(True))

        thread = threading.Thread(target=self._run, args=(slow_mo,), daemon=True)
        thread.start()
    
    def _run(self, slow_mo: int):
        try:
            logger.info("Iniciando Genesis...")

            root_path = Path(__file__).resolve().parent.parent.parent
            genesis_main = root_path / "genesis" / "main.py"

            env = os.environ.copy()
            env["ASI_SLOW_MO"] = str(slow_mo)

            self.process = subprocess.Popen(
                [sys.executable, str(genesis_main)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            if self.process.stdout:
                for line in self.process.stdout:
                    self._log_line(line)
            
            self.process.wait()

            logger.info("Genesis finalizado.")
        
        except Exception as e:
            logger.error("Erro ao executar Genesis: {}", e)
        
        finally:
            self.app.after(0, self._finish_execution)

    def _finish_execution(self):
        self.process = None
        self.is_running = False
        self.app._set_ui_running_state(False)
        

    def stop(self):
        if not self.is_running:
            return
        
        logger.info("Parando Genesis...")

        self.is_running = False
        self.app.after(0, lambda: self.app._set_ui_running_state(False))

        if self.process:
            threading.Thread(
                target=self._kill_process_tree,
                daemon=True
            ).start()
    

    def _kill_process_tree(self):

        process = self.process
        if process is None:
            return
        
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        except Exception as e:
            logger.error("Erro ao finalizar Genesis: {}", e)
        
        logger.info("Genesis parado.")


    def _log_line(self, line: str):

        line = line.strip()
        if not line:
            return

        try:
            log = json.loads(line)
            level = log.get("level", "INFO").lower()
            message = log.get("message", "")
            exception = log.get("exception", "")
            time = log.get("time", "")

            if exception:
                message = f"{message}\n{exception}"

            formatted = f"{time} | [GENESIS] | {level.upper()} | {message}"

            log_fn = getattr(logger, level, logger.info)
            log_fn(formatted)

        except json.JSONDecodeError:
            logger.info(line)
