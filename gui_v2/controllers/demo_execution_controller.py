"""Callbacks provisórios da execução visual, usando o catálogo real."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from pathlib import Path
import queue
import subprocess
import threading
import time
from datetime import datetime, timezone
from tkinter import messagebox

import customtkinter as ctk

from gui_v2.assets import create_target_icon, load_module_image
from gui_v2.controllers.app_controller import AppController
from gui_v2.models.execution import (
    ExecutionEvent,
    ExecutionEventLevel,
    ExecutionEventType,
    ExecutionProgress,
    ExecutionState,
)
from gui_v2.models.test_item import TestItem
from gui_v2.pages.execution_page import ExecutionPage
from gui_v2.services.catalog_service import CatalogService
from gui_v2.services.codegen_service import CodegenService
from gui_v2.services.configuration_service import (
    ClientConfiguration,
    ConfigurationService,
    ConfigurationSnapshot,
)
from gui_v2.services.history_service import HistoryService
from gui_v2.services.pytest_service import PytestService
from gui_v2.theme import COLORS


ROOT = Path(__file__).resolve().parents[2]
ICONS_DIR = ROOT / "gui" / "icons"
PRIMARY_MODULES = ("Almoxarifado", "Patrimônio", "Corporativo")
MODULE_PRESENTATION = {
    "Almoxarifado": (COLORS["orange"], "icon_almoxarifado.png"),
    "Patrimônio": (COLORS["purple"], "icon_patrimonio.png"),
    "Corporativo": (COLORS["teal"], "icon_corporativo_e_compras.png"),
}
# Acompanha o teto do painel: eventos além disso já não seriam exibidos.
LOG_HISTORY_LIMIT = 10_000


class DemoExecutionController:
    """Coordena a execução da GUI sem replicar dados do catálogo."""

    def __init__(
        self,
        host: ctk.CTk,
        speed_ms: int,
        on_speed_changed: Callable[[int], None],
        get_log_level: Callable[[], str] | None = None,
        get_browser_visible: Callable[[], bool] | None = None,
        get_full_output: Callable[[], bool] | None = None,
        on_full_output_changed: Callable[[bool], None] | None = None,
        get_logs_expanded: Callable[[], bool] | None = None,
        on_logs_expanded_changed: Callable[[bool], None] | None = None,
        can_start_execution: Callable[[], bool] | None = None,
        configuration: ConfigurationSnapshot | None = None,
    ) -> None:
        self._host = host
        self._speed_ms = speed_ms
        self._on_speed_changed = on_speed_changed
        self._get_log_level = get_log_level or (lambda: "INFO")
        self._get_browser_visible = get_browser_visible or (lambda: True)
        self._get_full_output = get_full_output or (lambda: False)
        self._on_full_output_changed = on_full_output_changed or (lambda _value: None)
        self._get_logs_expanded = get_logs_expanded or (lambda: False)
        self._on_logs_expanded_changed = on_logs_expanded_changed or (lambda _value: None)
        self._execution_log_level = "INFO"
        self._execution_browser_visible = True
        self._can_start_execution = can_start_execution or (lambda: True)
        self._state_controller = AppController()
        self._configuration = configuration or ConfigurationService().load()
        self._catalog_service = CatalogService()
        self._history_service = HistoryService()
        self._codegen_service = CodegenService()
        self._pytest_service = PytestService()
        self._catalog_items: tuple[TestItem, ...] = ()
        self._active_client = self._apply_client_configuration(
            self._configuration.active_client_key
        )
        self._history_by_path = self._load_history_for_client(self._active_client.key)
        self._module_images: dict[str, ctk.CTkImage] = {}
        self._process_events: queue.Queue[ExecutionEvent] | None = None
        self._execution_generation = 0
        self._poll_after_id: str | None = None
        self._pytest_saw_skip = False
        self._pytest_saw_pass = False
        self._stop_requested = False
        self._stop_thread: threading.Thread | None = None
        self._logs_expanded = self._get_logs_expanded()
        self._complete_logs = self._get_full_output()
        self._log_history: deque[ExecutionEvent] = deque(maxlen=LOG_HISTORY_LIMIT)
        self._progress: ExecutionProgress | None = None
        self._last_result: tuple[ExecutionState, str] | None = None
        self._page: ExecutionPage | None = None

    @property
    def is_running(self) -> bool:
        """Indica se há um teste Pytest conectado à interface em execução."""
        return self._process_events is not None

    def stop(self) -> None:
        """Interrompe o teste Pytest conectado à interface, se estiver ativo."""
        if self.is_running:
            self._stop_pytest()

    def stop_and_wait(self, timeout: float = 10.0) -> bool:
        """No fechamento, aguarda a parada sem liberar uma execução ainda viva."""
        self.stop()
        if self._stop_thread is not None:
            self._stop_thread.join(timeout)
        if self._poll_after_id is not None:
            self._host.after_cancel(self._poll_after_id)
            self._poll_after_id = None
        if self.is_running:
            self._poll_execution_events(self._execution_generation)
        return not self.is_running

    def create_page(
        self,
        master: ctk.CTkBaseClass,
    ) -> ExecutionPage:
        self._logs_expanded = self._get_logs_expanded()
        self._complete_logs = self._get_full_output()
        page = ExecutionPage(
            master,
            current_module=self._state_controller.state.current_module,
            primary_modules=PRIMARY_MODULES,
            module_colors=self._module_colors(),
            available_modules=self._other_module_names,
            image_loader=self._load_module_image,
            clients={client.key: client.label for client in self._configuration.clients},
            active_client_key=self._active_client.key,
            url=self._active_client.url,
            speed_ms=self._speed_ms,
            on_open_codegen=self._open_codegen,
            on_client_selected=self._select_client_configuration,
            on_speed_changed=self._change_speed,
            on_module_selected=self._select_module,
            on_test_toggled=self._toggle_test,
            on_section_toggled=self._toggle_section,
            on_clear_selection=self._clear_selected_tests,
            on_run=self._run_selected_test,
            on_stop=self._stop_pytest,
            on_toggle_logs=self._toggle_logs,
            on_toggle_log_mode=self._toggle_log_mode,
            on_clear_logs=self._clear_logs,
        )
        self._page = page
        self._render_catalog()
        self._render_selection()
        self._update_progress()
        page.set_complete_log_mode(self._complete_logs)
        page.set_logs_expanded(self._logs_expanded)
        page.set_running(self.is_running)
        if self._log_history:
            self._render_log_history()
        if self._last_result is not None:
            page.show_execution_result(self._last_result[0].value, self._last_result[1])
        return page

    def _active_page(self) -> ExecutionPage | None:
        return self._page if self._page is not None and self._page.winfo_exists() else None

    def _module_colors(self) -> dict[str, str]:
        return {item.module: self._module_color(item.module) for item in self._catalog_items}

    @staticmethod
    def _module_color(module: str) -> str:
        return MODULE_PRESENTATION.get(module, (COLORS["accent_light"], None))[0]

    def _load_module_image(self, module: str) -> ctk.CTkImage | None:
        if module in self._module_images:
            return self._module_images[module]
        _color, filename = MODULE_PRESENTATION.get(module, (COLORS["accent_light"], None))
        image = create_target_icon() if filename is None else load_module_image(ICONS_DIR, filename)
        if image is not None:
            self._module_images[module] = image
        return image

    def _other_module_names(self) -> list[str]:
        names = list(dict.fromkeys(item.module for item in self._catalog_items))
        others = [name for name in names if name not in PRIMARY_MODULES]
        return [name for name in others if name == "Testes Específicos"] + [
            name for name in others if name != "Testes Específicos"
        ]

    def _apply_client_configuration(
        self,
        requested_key: str | None,
        catalog_items: tuple[TestItem, ...] | None = None,
    ) -> ClientConfiguration:
        clients = self._configuration.clients
        if not clients:
            raise ValueError("Nenhum cliente foi configurado em configs.yaml.")
        client = next((item for item in clients if item.key == requested_key), clients[0])
        if catalog_items is None:
            catalog_items = self._catalog_service.load_items_for_client(
                client.key, client.version
            )
        if not catalog_items:
            raise ValueError(f"Cliente '{client.key}' não possui testes disponíveis.")
        available_modules = {item.module for item in catalog_items}

        self._state_controller.select_client(client.key)
        self._catalog_items = catalog_items
        self._state_controller.state.url = client.url
        if self._state_controller.state.current_module not in available_modules:
            self._state_controller.select_module(catalog_items[0].module)
        return client

    def _load_history_for_client(self, client_key: str) -> dict[str, str]:
        history = self._history_service.load_for_client(client_key)
        aggregated = self._history_service.aggregate_by_test_path(history)
        return {
            path: str(entry.get("resultado", "none"))
            for path, entry in aggregated.items()
        }

    def _select_client_configuration(self, client_key: str) -> None:
        """Troca o cliente ativo quando não há execução em andamento."""
        if self.is_running or client_key not in {
            client.key for client in self._configuration.clients
        }:
            return
        if self._active_client.key == client_key:
            return
        try:
            client = self._configuration.client(client_key)
            catalog_items = self._catalog_service.load_items_for_client(
                client.key, client.version
            )
            if not catalog_items:
                raise ValueError(
                    f"Cliente '{client.key}' não possui testes disponíveis."
                )
            ConfigurationService().set_active_client(client_key)
        except (OSError, ValueError, TypeError, KeyError) as error:
            messagebox.showerror(
                "Não foi possível selecionar o cliente",
                str(error),
                parent=self._host,
            )
            return
        self._active_client = self._apply_client_configuration(
            client_key, catalog_items
        )
        self._history_by_path = self._load_history_for_client(self._active_client.key)
        if page := self._active_page():
            page.set_client_configuration(
                self._active_client.key,
                self._active_client.url,
            )
            page.set_available_modules(self._module_colors(), self._state_controller.state.current_module)
            self._render_catalog()
            page.update_catalog_history(self._history_by_path)
        self._render_selection()

    def _change_speed(self, speed_ms: int) -> None:
        """Atualiza a velocidade corrente e delega sua persistência à aplicação."""
        self._speed_ms = speed_ms
        self._on_speed_changed(speed_ms)

    def _sections_for_current_module(self) -> dict[str, list[TestItem]]:
        sections: dict[str, list[TestItem]] = {}
        for item in self._catalog_items:
            if item.module == self._state_controller.state.current_module:
                sections.setdefault(item.section, []).append(item)
        return sections

    def _select_module(self, module: str) -> None:
        if module not in {item.module for item in self._catalog_items}:
            return
        if not self._state_controller.select_module(module):
            return
        if page := self._active_page():
            page.show_module(
                module,
                self._module_color(module),
                self._sections_for_current_module(),
                self._state_controller.state.selected_test_ids,
                self._history_by_path,
            )
        self._render_selection()

    def _render_catalog(self) -> None:
        if page := self._active_page():
            page.render_catalog(
                self._state_controller.state.current_module,
                self._module_color(self._state_controller.state.current_module),
                self._sections_for_current_module(),
                self._state_controller.state.selected_test_ids,
                self._history_by_path,
            )

    def _toggle_test(self, selection_id: str, selected: bool) -> None:
        if self.is_running:
            if page := self._active_page():
                page.set_tests_selected((selection_id,), self._state_controller.state.selected_test_ids)
            return
        self._state_controller.set_test_selected(selection_id, selected)
        if page := self._active_page():
            page.set_tests_selected(
                (selection_id,), self._state_controller.state.selected_test_ids
            )
        self._render_selection()

    def _toggle_section(self, selection_ids: tuple[str, ...]) -> None:
        if self.is_running:
            return
        self._state_controller.toggle_section(selection_ids)
        if page := self._active_page():
            page.set_tests_selected(
                selection_ids, self._state_controller.state.selected_test_ids
            )
        self._render_selection()

    def _clear_selected_tests(self) -> None:
        """Limpa a seleção e sincroniza os testes visíveis sem remontar o catálogo."""
        if self.is_running:
            return
        selected_ids = tuple(self._state_controller.state.selected_test_ids)
        if not selected_ids:
            return
        self._state_controller.clear_selected_tests()
        if page := self._active_page():
            page.set_tests_selected(selected_ids, self._state_controller.state.selected_test_ids)
        self._render_selection()

    def _render_selection(self) -> None:
        if not (page := self._active_page()):
            return
        selected_ids = self._state_controller.state.selected_test_ids
        seen_ids: set[str] = set()
        items: list[tuple[str, str]] = []
        for item in self._catalog_items:
            if item.selection_id not in selected_ids or item.selection_id in seen_ids:
                continue
            seen_ids.add(item.selection_id)
            items.append((item.name, item.module))
        page.render_selection(items)

    def _open_codegen(self) -> None:
        if not (page := self._active_page()):
            return
        try:
            self._codegen_service.launch(page.url)
        except ValueError as error:
            messagebox.showwarning("URL inválida", str(error), parent=self._host)
        except OSError as error:
            messagebox.showerror("Não foi possível abrir o Codegen", str(error), parent=self._host)

    def _run_selected_test(self) -> None:
        """Inicia os testes selecionados na ordem do catálogo."""
        if self.is_running:
            return
        if not self._can_start_execution():
            messagebox.showwarning(
                "Outra execução em andamento",
                "Interrompa a execução da Sentinela antes de iniciar o Pytest.",
                parent=self._host,
            )
            return
        selected_ids = self._state_controller.state.selected_test_ids
        if not selected_ids:
            messagebox.showwarning(
                "Selecione ao menos um teste",
                "Marque os testes que deseja executar.",
                parent=self._host,
            )
            return
        selected_items: list[TestItem] = []
        seen_ids: set[str] = set()
        for item in self._catalog_items:
            if item.selection_id in selected_ids and item.selection_id not in seen_ids:
                selected_items.append(item)
                seen_ids.add(item.selection_id)
        if seen_ids != selected_ids:
            messagebox.showwarning(
                "Teste indisponível",
                "Um ou mais testes selecionados não estão disponíveis no catálogo atual.",
                parent=self._host,
            )
            return
        targets = tuple(item.pytest_target for item in selected_items)

        self._execution_generation += 1
        generation = self._execution_generation
        self._pytest_saw_skip = False
        self._pytest_saw_pass = False
        self._stop_requested = False
        self._execution_log_level = self._get_log_level()
        self._execution_browser_visible = self._get_browser_visible()
        self._log_history.clear()
        self._last_result = None
        if page := self._active_page():
            page.clear_log()
            page.show_execution_result("", "")
        self._progress = ExecutionProgress(total_targets=len(targets))
        self._update_progress()
        self._state_controller.state.execution_state = ExecutionState.STARTING
        try:
            self._process_events = self._pytest_service.start(
                targets,
                speed_ms=self._speed_ms,
                browser_visible=self._execution_browser_visible,
                client_key=self._active_client.key,
            )
        except (OSError, RuntimeError, ValueError) as error:
            self._process_events = None
            self._state_controller.state.execution_state = ExecutionState.FAILED
            messagebox.showerror("Não foi possível iniciar os testes", str(error), parent=self._host)
            return
        self._state_controller.state.execution_state = ExecutionState.RUNNING
        if page := self._active_page():
            page.set_running(True)
        self._update_progress()
        self._schedule_event_poll(generation)

    def _schedule_event_poll(self, generation: int) -> None:
        """Agenda a leitura da fila sem bloquear a thread da interface."""
        self._poll_after_id = self._host.after(
            50,
            lambda: self._poll_execution_events(generation),
        )

    def _poll_execution_events(self, generation: int) -> None:
        """Consome eventos apenas da execução que iniciou este polling."""
        if generation != self._execution_generation or self._process_events is None:
            return
        self._poll_after_id = None
        log_parts: list[str] = []
        for _ in range(250):
            try:
                event = self._process_events.get_nowait()
            except queue.Empty:
                break
            if (
                event.event_type is ExecutionEventType.PROCESS_EXITED
                and self._stop_thread is not None
                and self._stop_thread.is_alive()
            ):
                self._process_events.put(event)
                break
            if event.event_type is ExecutionEventType.TEST_RESULT and event.message == "SKIPPED":
                self._pytest_saw_skip = True
            if event.event_type is ExecutionEventType.TEST_RESULT and event.message in {"PASSED", "XPASS"}:
                self._pytest_saw_pass = True
            self._update_progress_from_event(event)
            log_parts.append(self._append_process_event(event))
            if event.event_type is ExecutionEventType.PROCESS_EXITED:
                self._append_log("".join(log_parts))
                self._finish_pytest(event.return_code)
                return
        self._append_log("".join(log_parts))
        self._schedule_event_poll(generation)
        self._update_progress()

    def _finish_pytest(self, return_code: int | None) -> None:
        """Registra o resultado final do teste e libera a interface."""
        if self._stop_requested and self._pytest_service.last_stop_mode != "already_completed":
            state = ExecutionState.INTERRUPTED
            result = "Execução interrompida pelo usuário."
        else:
            state = self._pytest_service.classify_outcome(return_code, self._pytest_saw_skip, self._pytest_saw_pass)
            result = {
                ExecutionState.SUCCEEDED: "Execução concluída com sucesso.",
                ExecutionState.FAILED: "A execução falhou.",
                ExecutionState.SKIPPED: "A execução foi ignorada (skip).",
            }.get(state, "Execução finalizada.")
            if state is ExecutionState.SUCCEEDED and self._pytest_saw_skip:
                result = "Execução concluída com teste(s) ignorado(s)."
        self._state_controller.state.execution_state = state
        self._last_result = (state, result)
        finished_at = time.monotonic()
        if self._progress is not None:
            self._progress.finished_at = finished_at
            self._progress.current_target = None
        self._update_progress()
        result_event = ExecutionEvent(
            ExecutionEventType.EXECUTION_FINISHED,
            ExecutionEventLevel.ERROR if state is ExecutionState.FAILED else ExecutionEventLevel.INFO,
            result,
            timestamp=datetime.now(timezone.utc),
            monotonic_time=finished_at,
        )
        self._log_history.append(result_event)
        self._render_process_event(result_event)
        if state in {
            ExecutionState.SUCCEEDED,
            ExecutionState.FAILED,
            ExecutionState.SKIPPED,
        }:
            self._history_by_path = self._load_history_for_client(self._active_client.key)
        self._process_events = None
        self._poll_after_id = None
        if page := self._active_page():
            page.set_running(False)
            page.show_execution_result(state.value, result)
            page.update_catalog_history(self._history_by_path)

    def _append_process_event(self, event: ExecutionEvent) -> str:
        """Guarda o evento no histórico e devolve o texto a exibir no lote do tick."""
        if event.event_type is ExecutionEventType.PROCESS_EXITED:
            return ""
        self._log_history.append(event)
        return self._format_process_event(event)

    def _update_progress_from_event(self, event: ExecutionEvent) -> None:
        """Atualiza contadores somente a partir de eventos de teste reconhecidos."""
        if self._progress is None:
            return
        if (
            event.event_type is ExecutionEventType.COLLECTION_COMPLETED
            and event.count is not None
        ):
            self._progress.total_targets = event.count
            if self._progress.started_at is None:
                self._progress.started_at = event.monotonic_time
        elif event.event_type is ExecutionEventType.TEST_STARTED:
            self._progress.current_target = event.target
        elif event.event_type is ExecutionEventType.TEST_RESULT:
            self._progress.completed_targets += 1
            self._progress.current_target = None

    def _update_progress(self) -> None:
        """Envia dados medidos/reconhecidos à página sem inferir resultados ausentes."""
        progress = self._progress
        if progress is None:
            return
        completed: int | None = (
            progress.completed_targets
            if progress.started_at is not None
            and progress.completed_targets <= progress.total_targets
            else None
        )
        if page := self._active_page():
            page.set_progress(
                completed,
                progress.total_targets,
                progress.current_target,
                progress.duration_seconds,
            )

    def _stop_pytest(self) -> None:
        """Solicita parada em uma thread e mantém o Tk disponível para interação."""
        if self._process_events is None or (self._stop_thread is not None and self._stop_thread.is_alive()):
            return
        self._stop_requested = True
        self._state_controller.state.execution_state = ExecutionState.STOPPING
        self._stop_thread = threading.Thread(
            target=self._stop_worker,
            args=(self._pytest_service, self._process_events),
            name="gui-pytest-stop",
            daemon=True,
        )
        self._stop_thread.start()

    @staticmethod
    def _stop_worker(service: PytestService, events: queue.Queue[ExecutionEvent]) -> None:
        """Publica falhas de parada na fila, sem tocar em widgets."""
        try:
            service.stop(timeout=10)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            events.put(ExecutionEvent(
                ExecutionEventType.STDERR, ExecutionEventLevel.ERROR,
                f"Não foi possível confirmar o encerramento do Pytest: {error}",
            ))

    def _append_log(self, text: str) -> None:
        if page := self._active_page():
            page.append_log(text)

    def _toggle_logs(self) -> None:
        self._logs_expanded = not self._logs_expanded
        if page := self._active_page():
            page.set_logs_expanded(self._logs_expanded)
            if self._logs_expanded:
                page.after_idle(page.scroll_to_logs)
        self._on_logs_expanded_changed(self._logs_expanded)

    def _toggle_log_mode(self) -> None:
        """Alterna entre eventos essenciais e saída original completa."""
        self.set_full_output(not self._complete_logs)
        self._on_full_output_changed(self._complete_logs)

    def set_full_output(self, complete: bool) -> None:
        """Sincroniza o modo de log com a preferência da aplicação."""
        if self._complete_logs == complete:
            return
        self._complete_logs = complete
        if page := self._active_page():
            page.set_complete_log_mode(complete)
            self._render_log_history()

    def _clear_logs(self) -> None:
        """Limpa o histórico usado na alternância entre modos."""
        self._log_history.clear()

    def _render_log_history(self) -> None:
        """Redesenha o histórico com uma única inserção no painel."""
        if page := self._active_page():
            page.clear_log()
            self._append_log("".join(map(self._format_process_event, self._log_history)))

    def _render_process_event(self, event: ExecutionEvent) -> None:
        """Renderiza um evento conforme o modo de log atualmente selecionado."""
        self._append_log(self._format_process_event(event))

    def _format_process_event(self, event: ExecutionEvent) -> str:
        """Formata um evento conforme o modo de log selecionado; vazio se oculto."""
        threshold = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
        }.get(self._execution_log_level, 1)
        rank = {
            ExecutionEventLevel.DEBUG: 0,
            ExecutionEventLevel.INFO: 1,
            ExecutionEventLevel.WARNING: 2,
            ExecutionEventLevel.ERROR: 3,
        }[event.level]
        if rank < threshold:
            return ""
        if event.event_type is ExecutionEventType.PROCESS_EXITED:
            return ""
        if self._complete_logs:
            if event.raw_message is not None:
                return event.raw_message + "\n"
            if event.event_type in {
                ExecutionEventType.EXECUTION_STARTED,
                ExecutionEventType.EXECUTION_FINISHED,
            }:
                return event.message + "\n"
            if event.event_type not in {
                ExecutionEventType.TEST_STARTED,
                ExecutionEventType.TEST_RESULT,
                ExecutionEventType.PYTEST_SUMMARY,
            }:
                return event.message + "\n"
            return ""
        label: str
        if event.event_type is ExecutionEventType.EXECUTION_STARTED:
            label, message = "Início", event.message
        elif event.event_type is ExecutionEventType.TEST_STARTED:
            label, message = "Teste atual", event.target or event.message
        elif event.event_type is ExecutionEventType.TEST_RESULT:
            label, message = "Resultado", f"{event.target}: {event.message}"
        elif event.event_type is ExecutionEventType.PYTEST_SUMMARY:
            label, message = "Resumo", event.message
        elif event.event_type is ExecutionEventType.EXECUTION_FINISHED:
            label, message = "Resultado final", event.message
        elif event.event_type is ExecutionEventType.COLLECTION_COMPLETED:
            return ""
        else:
            if event.level not in {ExecutionEventLevel.WARNING, ExecutionEventLevel.ERROR}:
                return ""
            label, message = event.level.value, event.message
        timestamp = event.timestamp.astimezone().strftime("%H:%M:%S")
        return f"{timestamp} | {label} | {message}\n"
