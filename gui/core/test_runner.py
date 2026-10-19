import os
import subprocess
import threading

from loguru import logger


class TestRunner:
    def __init__(self, app):
        """
        app -> reference to Tk App
        Used only for UI callbacks and logging.
        """
        self.app = app
        self.current_process = None
        self.is_running = False
    

    def get_project_root(self):
        return os.getcwd()
    

    def get_python_executable(self):
        return os.path.join(
            self.get_project_root(),
            ".venv",
            "Scripts",
            "python.exe"
        )
    

    def run(self, test_files, slow_mo: int = 0):
        """
        Start execution in background thread.
        
        :param test_files: Lista de caminhos absolutos dos testes a executar.
        :param slow_mo: Atraso em ms entre ações do Playright (0 = sem atraso).
        """
        if self.is_running:
            return
        
        self.is_running = True

        # Lock UI safely (must be main thread)
        self.app.after(0, lambda: self.app._set_ui_running_state(True))

        threading.Thread(
            target=self._run_test_sequence,
            args=(test_files, slow_mo),
            daemon=True
        ).start()


    def stop(self):
        if not self.is_running:
            return

        logger.info("Parando testes...")

        self.is_running = False

        # Disable UI immediately (safe call)
        self.app.after(0, lambda: self.app._set_ui_running_state(False))

        if self.current_process:
            threading.Thread(
                target=self._kill_process_tree,
                daemon=True
            ).start()


    def _kill_process_tree(self):
        process = self.current_process
        if process is None:
            return
        
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            logger.error("Erro ao finalizar processo: {}", e)

        logger.info("Testes parados.")
    

    def _run_test_sequence(self, test_files, slow_mo: int):
        try:
            python_exe = self.get_python_executable()
            project_root = self.get_project_root()

            cmd = [
                python_exe,
                "-m",
                "pytest",
                *test_files, # all tests passed at once
                "-x",
                "-p", "no:randomly", # preserve GUI's order
            ]

            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            # Passa a velocidade escolhida na GUI para o conftest.py
            env["ASI_SLOW_MO"] = str(slow_mo)
            # A GUI antiga mantém o comportamento histórico de pausar na falha.
            env["ASI_PAUSAR_NA_FALHA"] = "1"

            self.current_process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP
                    | subprocess.CREATE_NO_WINDOW
                ),
            )

            # ---- Live stream ----
            if self.current_process.stdout:
                for line in self.current_process.stdout:

                    if not self.is_running:
                        break

                    line = line.rstrip()

                    level = "INFO"

                    # Cosmetic highlighting only
                    if "ERROR" in line or line.startswith("FAILED"):
                        level = "ERROR"
                    elif "SUCCESS" in line:
                        level = "SUCCESS"
                    elif "WARNING" in line:
                        level = "WARNING"
                    elif "DEBUG" in line:
                        level = "DEBUG"

                    # Rota B: stdout do pytest vai direto para app.log, sem passar pelo Loguru.
                    # Filtros no GuiLogSink não têm efeito aqui.
                    self.app.log(line, level)

            # Ensure process finished
            return_code = self.current_process.wait()

            if return_code != 0:
                logger.error("Execução finalizada com falha (code={})", return_code)
            else:
                logger.info("Testes finalizados.")
        finally:
            # Reset UI on main thread
            self.app.after(0, self._finish_execution)
    

    def _finish_execution(self):
        self.current_process = None
        self.is_running = False
        self.app._set_ui_running_state(False)
