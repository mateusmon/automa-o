"""Registro local de erros internos da GUI v2."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import tempfile
import threading
from types import TracebackType
import warnings


GUI_LOGGER_NAME = "gui_v2"
LOG_DIRECTORY = Path(__file__).resolve().parents[1] / "logs"
LOG_PATH = LOG_DIRECTORY / "gui_errors.log"
MAX_LOG_BYTES = 1_048_576
BACKUP_COUNT = 5
_MANAGED_HANDLER_ATTRIBUTE = "_asi_gui_error_handler"
_ProcessExceptionHook = Callable[
    [type[BaseException], BaseException, TracebackType | None], None
]
_ThreadExceptionHook = Callable[[threading.ExceptHookArgs], None]
_previous_process_hook: _ProcessExceptionHook = sys.excepthook
_previous_thread_hook: _ThreadExceptionHook = threading.excepthook
_active_error_service: GuiErrorService | None = None


def _log_uncaught_exception(
    service: GuiErrorService | None,
    source: str,
    exception_type: type[BaseException],
    exception: BaseException,
    traceback: TracebackType | None,
) -> None:
    if (
        service is None
        or not service.configured
        or not issubclass(exception_type, Exception)
    ):
        return
    try:
        service.logger.error(
            "Exceção não tratada em %s.",
            source,
            exc_info=(exception_type, exception, traceback),
        )
    except Exception:
        # A falha do logger não deve substituir a exceção original nem sua cadeia.
        return


def _process_exception_hook(
    exception_type: type[BaseException],
    exception: BaseException,
    traceback: TracebackType | None,
) -> None:
    _log_uncaught_exception(
        _active_error_service,
        "processo principal",
        exception_type,
        exception,
        traceback,
    )
    _previous_process_hook(exception_type, exception, traceback)


def _thread_exception_hook(arguments: threading.ExceptHookArgs) -> None:
    _log_uncaught_exception(
        _active_error_service,
        f"thread {arguments.thread.name if arguments.thread else 'desconhecida'}",
        arguments.exc_type,
        arguments.exc_value,
        arguments.exc_traceback,
    )
    _previous_thread_hook(arguments)


@dataclass(frozen=True, slots=True)
class GuiErrorLogSnapshot:
    """Conteúdo disponível para consulta ou motivo de indisponibilidade."""

    content: str = ""
    error_message: str | None = None
    signature: str = ""

    @property
    def available(self) -> bool:
        """Indica se a leitura do histórico pôde ser concluída."""
        return self.error_message is None


class _GuiRotatingFileHandler(RotatingFileHandler):
    """Comunica falhas de escrita sem encaminhá-las ao próprio logger."""

    def __init__(
        self,
        filename: str | Path,
        *,
        max_bytes: int,
        backup_count: int,
        encoding: str,
        delay: bool,
        on_error: Callable[[Exception], None],
    ) -> None:
        self._on_error = on_error
        super().__init__(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
            delay=delay,
        )

    def handleError(self, record: logging.LogRecord) -> None:
        error = sys.exc_info()[1]
        if isinstance(error, Exception):
            self._on_error(error)
        super().handleError(record)


class GuiErrorService:
    """Configura o arquivo de diagnóstico e lê o histórico rotacionado."""

    def __init__(self, log_path: Path = LOG_PATH) -> None:
        self._log_path = Path(log_path)
        self._seen_path = self._log_path.parent / "gui_errors_seen.txt"
        self._logger = logging.getLogger(GUI_LOGGER_NAME)
        self._configuration_error: str | None = None
        self._configured = False
        self._warning_emitted = False
        self._seen_signature = self._load_seen_signature()

    @property
    def log_path(self) -> Path:
        """Caminho absoluto do arquivo ativo de erros da GUI."""
        return self._log_path

    @property
    def configured(self) -> bool:
        """Informa se o handler de arquivo foi instalado."""
        return self._configured

    @property
    def logger(self) -> logging.Logger:
        """Logger nomeado usado pelos hooks e componentes da GUI v2."""
        return self._logger

    @property
    def has_unseen_errors(self) -> bool:
        """Indica se o conjunto atual de arquivos difere do último conjunto visto."""
        if self._configuration_error is not None:
            return True
        signature, error = self._current_log_signature()
        return error is not None or bool(signature and signature != self._seen_signature)

    def _log_paths(self) -> list[Path]:
        paths = [
            Path(f"{self._log_path}.{index}")
            for index in range(BACKUP_COUNT, 0, -1)
        ]
        paths.append(self._log_path)
        return paths

    def _current_log_signature(self) -> tuple[str, str | None]:
        """Assina tamanho e data dos arquivos para detectar novos registros."""
        entries: list[str] = []
        for path in self._log_paths():
            try:
                stat = path.stat()
            except FileNotFoundError:
                continue
            except OSError as error:
                return "", str(error)
            if stat.st_size:
                entries.append(f"{path.name}:{stat.st_size}:{stat.st_mtime_ns}")
        return "|".join(entries), None

    def _load_seen_signature(self) -> str:
        """Carrega o marcador local; ausência/corrupção faz erros antigos reaparecerem."""
        try:
            return self._seen_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError):
            return ""

    def mark_viewed(self, snapshot: GuiErrorLogSnapshot) -> bool:
        """Persiste a assinatura exata que a pessoa acabou de consultar."""
        if not snapshot.available:
            return False

        temporary_path: Path | None = None
        try:
            self._seen_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._seen_path.parent,
                prefix=".gui_errors_seen.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                stream.write(snapshot.signature)
            os.replace(temporary_path, self._seen_path)
            self._seen_signature = snapshot.signature
            return True
        except OSError:
            return False
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def clear(self) -> str | None:
        """Limpa o arquivo ativo e as cópias rotacionadas; retorna erro, se houver."""
        handler = next(
            (
                item
                for item in self._logger.handlers
                if getattr(item, _MANAGED_HANDLER_ATTRIBUTE, False)
                and Path(item.baseFilename).resolve() == self._log_path.resolve()
            ),
            None,
        )
        if handler is None or not self._configured:
            return self._configuration_error or "O registro de erros não está disponível."

        handler.acquire()
        try:
            handler.close()
            for path in self._log_paths():
                path.unlink(missing_ok=True)
        except OSError as error:
            return str(error)
        finally:
            handler.release()
        return None

    def log_uncaught_exception(
        self,
        source: str,
        exception_type: type[BaseException],
        exception: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        """Registra uma exceção inesperada sem deixar falhas de logging escaparem."""
        _log_uncaught_exception(
            self, source, exception_type, exception, traceback
        )

    def install_global_exception_hooks(self) -> None:
        """Encadeia os hooks de processo/thread uma única vez."""
        global _active_error_service, _previous_process_hook, _previous_thread_hook

        _active_error_service = self
        if sys.excepthook is not _process_exception_hook:
            _previous_process_hook = sys.excepthook
            sys.excepthook = _process_exception_hook
        if threading.excepthook is not _thread_exception_hook:
            _previous_thread_hook = threading.excepthook
            threading.excepthook = _thread_exception_hook

    def restore_global_exception_hooks(self) -> None:
        """Restaura hooks anteriores se a GUI ainda for dona dos pontos globais."""
        global _active_error_service

        if sys.excepthook is _process_exception_hook:
            sys.excepthook = _previous_process_hook
        if threading.excepthook is _thread_exception_hook:
            threading.excepthook = _previous_thread_hook
        if _active_error_service is self:
            _active_error_service = None

    def configure(self) -> bool:
        """Instala um handler rotativo sem configurar nem alterar o logger root."""
        self._logger.setLevel(logging.ERROR)
        self._logger.propagate = False

        try:
            resolved_path = self._log_path.resolve()
            for handler in tuple(self._logger.handlers):
                if not getattr(handler, _MANAGED_HANDLER_ATTRIBUTE, False):
                    continue
                if (
                    Path(handler.baseFilename) == resolved_path
                    and self._configuration_error is None
                ):
                    if isinstance(handler, _GuiRotatingFileHandler):
                        handler._on_error = self._record_write_error
                    self._configured = True
                    return True
                self._logger.removeHandler(handler)
                handler.close()

            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            handler = _GuiRotatingFileHandler(
                self._log_path,
                max_bytes=MAX_LOG_BYTES,
                backup_count=BACKUP_COUNT,
                encoding="utf-8",
                delay=True,
                on_error=self._record_write_error,
            )
        except (OSError, RuntimeError) as error:
            self._configured = False
            self._record_write_error(error)
            return False

        handler.setLevel(logging.ERROR)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        setattr(handler, _MANAGED_HANDLER_ATTRIBUTE, True)
        self._logger.addHandler(handler)
        self._configured = True
        self._configuration_error = None
        return True

    def _record_write_error(self, error: Exception) -> None:
        """Guarda a falha para a futura tela e emite no máximo um aviso local."""
        self._configuration_error = str(error)
        self._configured = False
        if self._warning_emitted:
            return
        self._warning_emitted = True
        try:
            warnings.warn(
                f"O log interno da GUI está indisponível: {error}",
                RuntimeWarning,
                stacklevel=2,
            )
        except Warning:
            pass

    def read(self) -> GuiErrorLogSnapshot:
        """Lê cópias antigas e o arquivo ativo em ordem cronológica."""
        signature, signature_error = self._current_log_signature()
        if self._configuration_error is not None:
            return GuiErrorLogSnapshot(
                error_message=self._configuration_error,
                signature=signature,
            )
        if signature_error is not None:
            return GuiErrorLogSnapshot(
                error_message=signature_error,
                signature=signature,
            )

        contents: list[str] = []
        for path in self._log_paths():
            try:
                with path.open(encoding="utf-8") as stream:
                    contents.append(stream.read())
            except FileNotFoundError:
                continue
            except (OSError, UnicodeDecodeError) as error:
                return GuiErrorLogSnapshot(
                    error_message=str(error),
                    signature=signature,
                )

        return GuiErrorLogSnapshot(
            content="".join(contents),
            signature=signature,
        )
