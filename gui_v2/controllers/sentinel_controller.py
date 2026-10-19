"""Coordena a seleção de cliente e jornada na página Sentinela."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
import queue
import subprocess
import threading
import time
from uuid import uuid4
import logging
import customtkinter as ctk

from gui_v2.pages.sentinel_page import SentinelPage
from gui_v2.services.configuration_service import (
    ClientConfiguration,
    ConfigurationService,
    ConfigurationSnapshot,
)
from gui_v2.services.sentinel_plan_service import (
    SentinelModule,
    SentinelPlan,
    SentinelPlanService,
)
from gui_v2.models.test_item import TestItem
from gui_v2.services.catalog_service import CatalogService
from gui_v2.models.execution import (
    ExecutionEvent,
    ExecutionEventLevel,
    ExecutionEventType,
    ExecutionRecord,
    ExecutionSnapshot,
    ExecutionState,
    event_belongs_to_execution,
)
from gui_v2.services.sentinel_command_service import (
    SentinelCommandService,
    SentinelExecutionService,
    SentinelRunMode,
)
from gui_v2.services.sentinel_artifact_service import (
    MAX_HISTORY_RUNS,
    SentinelArtifactService,
    SentinelHistoryRun,
    SentinelRunArtifacts,
)
from gui_v2.services.execution_registry import ExecutionRegistry
from gui_v2.services.process_supervisor import ProcessMetrics
from gui_v2.services.sentinel_control_service import SentinelControlService


_LOGGER = logging.getLogger(__name__)
_CONTROL_EVENT_PREFIX = "ASI_GUI_STATE:"
# Traces chegam à pasta do run sem linha na saída; re-listá-los neste intervalo.
_TRACE_REFRESH_SECONDS = 2.0


@dataclass(slots=True)
class _ArtifactScan:
    """Estado da localização incremental de artefatos de uma execução."""

    scanned_lines: int
    listed_at: float
    artifacts: SentinelRunArtifacts
    announced: bool  # já houve linha de pasta/relatório na saída


class SentinelController:
    """Carrega os dados da Sentinela e atualiza a página ao trocar cliente."""

    def __init__(
        self,
        can_start_execution: Callable[[], bool] | None = None,
        ttl_days: int | None = None,
        get_logs_expanded: Callable[[], bool] | None = None,
        on_logs_expanded_changed: Callable[[bool], None] | None = None,
        configuration: ConfigurationSnapshot | None = None,
    ) -> None:
        self._configuration = configuration or ConfigurationService().load()
        if not self._configuration.clients:
            raise ValueError("Nenhum cliente foi configurado em configs.yaml.")
        self._plan_service = SentinelPlanService()
        self._catalog_service = CatalogService()
        self._available_tests: tuple[TestItem, ...] = ()
        self._selected_test: TestItem | None = None
        self._parallel_tests: list[TestItem] = []
        self._mode = SentinelRunMode.JOURNEY
        self._count = 1
        self._run_all_clients = False
        self._eligible_client_keys: tuple[str, ...] = ()
        self._retry_limit = SentinelCommandService.load_retry_limit()
        if ttl_days is None:
            self._ttl_days = SentinelCommandService.load_ttl_default()
        elif type(ttl_days) is int and 1 <= ttl_days <= 365:
            self._ttl_days = ttl_days
        else:
            raise ValueError("A retenção dos runs deve ser um inteiro entre 1 e 365 dias.")
        self._can_start_execution = can_start_execution or (lambda: True)
        self._get_logs_expanded = get_logs_expanded or (lambda: False)
        self._on_logs_expanded_changed = on_logs_expanded_changed or (lambda _value: None)
        self._clients = {client.key: client for client in self._configuration.clients}
        requested_key = self._configuration.active_client_key
        self._active_client = self._clients.get(requested_key, self._configuration.clients[0])
        self._available_tests = self._load_tests(self._active_client)
        self._page: SentinelPage | None = None
        self._host: ctk.CTkBaseClass | None = None
        self._execution_registry = ExecutionRegistry()
        self._artifact_service = SentinelArtifactService()
        self._history_runs: tuple[SentinelHistoryRun, ...] = self._load_history_runs()
        self._history_output_by_id = {
            run.execution_id: self._artifact_service.read_history_output(run)
            for run in self._history_runs
        }
        self._control_service = SentinelControlService()
        self._artifacts = SentinelRunArtifacts(None, None)
        self._selected_execution_id: str | None = (
            self._history_runs[0].execution_id if self._history_runs else None
        )
        self._plans: dict[str, SentinelPlan] = {}
        self._artifacts_by_execution: dict[str, SentinelRunArtifacts] = {}
        self._artifact_scans: dict[str, _ArtifactScan] = {}
        self._run_artifact_ids: set[str] = set()
        self._stop_requested_ids: set[str] = set()
        self._stop_threads: dict[str, threading.Thread] = {}
        self._exit_requeue_pending: set[str] = set()
        self._stop_completion_events: dict[str, threading.Event] = {}
        self._poll_after_id: str | None = None
        self._last_metrics_sample_at = 0.0

    @property
    def is_running(self) -> bool:
        """Indica se existe um processo Sentinela supervisionado ativo."""
        return bool(self._execution_registry.running_records())

    def create_page(
        self,
        master: ctk.CTkBaseClass,
    ) -> SentinelPage:
        """Cria a página com o cliente ativo e suas jornadas disponíveis."""
        clients = {client.key: client.label for client in self._configuration.clients}
        client_labels = self._client_labels()
        self._host = master.winfo_toplevel()
        modules = self._load_modules(self._active_client)
        tests = self._load_tests(self._active_client)
        page = SentinelPage(
            master,
            clients=clients,
            active_client_key=self._active_client.key,
            modules=modules,
            tests=tests,
            on_mode_selected=self._select_mode,
            on_test_selected=self._select_test,
            on_count_selected=self._select_count,
            on_all_clients_selected=self._select_all_clients,
            retry_limit=self._retry_limit,
            on_client_selected=self._select_client,
            on_module_selected=self._select_module,
            on_start=self.start,
            on_stop=self.request_stop,
            on_pause=self.toggle_pause,
            on_open_report=self.open_report,
            on_open_folder=self.open_folder,
            on_open_trace=self.open_trace,
            on_execution_selected=self._select_execution,
            on_test_toggled=self._toggle_parallel_test,
            on_test_removed=self._remove_parallel_test,
            on_toggle_logs=self._toggle_logs,
        )
        self._page = page
        page.set_logs_expanded(self._get_logs_expanded())
        page.set_mode(self._mode)
        page.set_count(self._count)
        if self._mode is SentinelRunMode.SPECIFIC_TEST:
            page.set_selected_test(self._selected_test)
            page.set_parallel_tests(self._parallel_tests)
            page.set_eligible_clients(
                tuple(client_labels[key] for key in self._eligible_client_keys)
            )
            page.set_run_all_clients(self._run_all_clients)
        self._sync_execution_panel()
        if self._plans:
            page.restore_selections(tuple(self._plans.values()))
        if self.is_running:
            page.set_running(True, None if self._plans else "Sentinela em execução…")
        elif hasattr(self, "_last_status"):
            page.set_running(False, None if self._plans else self._last_status)
        return page

    def _load_history_runs(self) -> tuple[SentinelHistoryRun, ...]:
        """Carrega os vinte runs recentes dentro do TTL configurado."""
        try:
            return self._artifact_service.discover_history(
                MAX_HISTORY_RUNS, ttl_days=self._ttl_days
            )
        except OSError as error:
            _LOGGER.warning("Não foi possível carregar o histórico da Sentinela: %s", error)
            return ()

    def _refresh_history_if_removed(self) -> None:
        """Atualiza o histórico quando a limpeza por TTL removeu alguma pasta."""
        if not any(not run.folder_path.is_dir() for run in self._history_runs):
            return
        self._history_runs = self._load_history_runs()
        self._history_output_by_id = {
            run.execution_id: self._artifact_service.read_history_output(run)
            for run in self._history_runs
        }

    def _toggle_logs(self) -> None:
        """Alterna o tamanho do painel e persiste a escolha da Sentinela."""
        expanded = not self._get_logs_expanded()
        if self._page is not None and self._page.winfo_exists():
            self._page.set_logs_expanded(expanded)
            if expanded:
                self._page.after_idle(self._page.scroll_to_logs)
        self._on_logs_expanded_changed(expanded)

    def _client_labels(self) -> dict[str, str]:
        """Mapeia rótulos sem colisão para as chaves de cliente."""
        labels = Counter(client.label for client in self._configuration.clients)
        return {
            client.key: (
                f"{client.label} ({client.key})"
                if labels[client.label] > 1
                else client.label
            )
            for client in self._configuration.clients
        }

    def _load_modules(
        self, client: ClientConfiguration
    ) -> tuple[SentinelModule, ...]:
        return self._plan_service.load_modules_for_client(client.key, client.version)

    def _load_tests(self, client: ClientConfiguration) -> tuple[TestItem, ...]:
        """Carrega os arquivos elegíveis no catálogo para o cliente ativo."""
        return self._catalog_service.load_items_for_client(client.key, client.version)

    def _select_mode(self, mode: SentinelRunMode) -> None:
        if self.is_running or mode == self._mode:
            return
        self._mode = mode
        self._count = 1
        self._run_all_clients = False
        self._eligible_client_keys = ()
        self._plans.clear()
        self._selected_test = None
        self._parallel_tests.clear()
        if self._page is not None and self._page.winfo_exists():
            self._page.set_mode(mode)

    def _select_count(self, count: int) -> None:
        if self.is_running or type(count) is not int or count not in (1, 2, 3):
            return
        self._count = count
        if self._page is not None and self._page.winfo_exists():
            self._page.set_count(count)

    def set_ttl_days(self, ttl_days: int) -> None:
        """Atualiza o TTL dos próximos comandos e do histórico visível."""
        if type(ttl_days) is not int or not 1 <= ttl_days <= 365:
            raise ValueError("A retenção dos runs deve ser um inteiro entre 1 e 365 dias.")
        self._ttl_days = ttl_days
        self._history_runs = self._load_history_runs()
        self._history_output_by_id = {
            run.execution_id: self._artifact_service.read_history_output(run)
            for run in self._history_runs
        }
        selected_id = self._selected_execution_id
        if (
            self._execution_registry.get(selected_id or "") is None
            and not any(run.execution_id == selected_id for run in self._history_runs)
        ):
            self._selected_execution_id = (
                self._history_runs[0].execution_id if self._history_runs else None
            )
        if self._page is not None and self._page.winfo_exists():
            self._sync_execution_panel()

    def _select_all_clients(self, enabled: bool) -> None:
        if self.is_running or self._mode is not SentinelRunMode.SPECIFIC_TEST:
            return
        self._run_all_clients = enabled
        if enabled and self._parallel_tests:
            self._parallel_tests.clear()
            if self._page is not None and self._page.winfo_exists():
                self._page.set_parallel_tests(())

    def _select_test(self, selection_id: str) -> None:
        if self.is_running:
            return
        self._selected_test = next(
            (item for item in self._available_tests if item.selection_id == selection_id),
            None,
        )
        self._eligible_client_keys = self._eligible_clients_for_test(self._selected_test)
        if self._page is not None and self._page.winfo_exists():
            self._page.set_selected_test(self._selected_test)
            if self._mode is SentinelRunMode.SPECIFIC_TEST:
                self._page.set_parallel_tests(self._parallel_tests)
            labels = self._client_labels()
            self._page.set_eligible_clients(
                tuple(labels[key] for key in self._eligible_client_keys)
            )

    def _toggle_parallel_test(self, selection_id: str) -> None:
        """Alterna um teste disponível no lote paralelo, limitado a dois paths."""
        if (
            self.is_running
            or self._mode is not SentinelRunMode.SPECIFIC_TEST
        ):
            return
        item = next(
            (test for test in self._available_tests if test.selection_id == selection_id),
            None,
        )
        if item is None:
            return
        if self._run_all_clients:
            if self._selected_test is not None and self._selected_test.path == item.path:
                self._selected_test = None
            elif self._selected_test is None:
                self._selected_test = item
            else:
                if self._page is not None and self._page.winfo_exists():
                    self._page.show_selection_notice(
                        "No modo multi-cliente, selecione somente um teste."
                    )
                return
            self._eligible_client_keys = self._eligible_clients_for_test(
                self._selected_test
            )
            if self._page is not None and self._page.winfo_exists():
                self._page.set_selected_test(self._selected_test)
                labels = self._client_labels()
                self._page.set_eligible_clients(
                    tuple(labels[key] for key in self._eligible_client_keys)
                )
            return
        if any(existing.path == item.path for existing in self._parallel_tests):
            self._parallel_tests = [
                existing for existing in self._parallel_tests if existing.path != item.path
            ]
            self._selected_test = self._parallel_tests[0] if self._parallel_tests else None
            self._eligible_client_keys = self._eligible_clients_for_test(self._selected_test)
            if self._page is not None and self._page.winfo_exists():
                self._page.set_parallel_tests(self._parallel_tests)
                self._page.set_selected_test(self._selected_test)
                labels = self._client_labels()
                self._page.set_eligible_clients(
                    tuple(labels[key] for key in self._eligible_client_keys)
                )
            return
        if self._parallel_tests and self._count != 1:
            if self._page is not None and self._page.winfo_exists():
                self._page.show_selection_notice("Duas execuções paralelas exigem Repetir teste = 1.")
            return
        if len(self._parallel_tests) >= 2:
            if self._page is not None and self._page.winfo_exists():
                self._page.show_selection_notice("O lote aceita no máximo dois testes.")
            return
        self._parallel_tests.append(item)
        self._selected_test = self._parallel_tests[0]
        self._eligible_client_keys = self._eligible_clients_for_test(self._selected_test)
        if self._page is not None and self._page.winfo_exists():
            self._page.set_parallel_tests(self._parallel_tests)
            self._page.set_selected_test(self._selected_test)
            labels = self._client_labels()
            self._page.set_eligible_clients(
                tuple(labels[key] for key in self._eligible_client_keys)
            )

    def _remove_parallel_test(self, selection_id: str) -> None:
        """Remove do lote o arquivo indicado e sincroniza o teste ativo."""
        if (
            self.is_running
            or self._mode is not SentinelRunMode.SPECIFIC_TEST
            or self._run_all_clients
        ):
            return
        item = next(
            (test for test in self._available_tests if test.selection_id == selection_id),
            None,
        )
        if item is None:
            return
        if not any(test.path == item.path for test in self._parallel_tests):
            return
        self._parallel_tests = [test for test in self._parallel_tests if test.path != item.path]
        self._selected_test = self._parallel_tests[0] if self._parallel_tests else None
        self._eligible_client_keys = self._eligible_clients_for_test(self._selected_test)
        if self._page is not None and self._page.winfo_exists():
            self._page.set_parallel_tests(self._parallel_tests)
            self._page.set_selected_test(self._selected_test)
            labels = self._client_labels()
            self._page.set_eligible_clients(
                tuple(labels[key] for key in self._eligible_client_keys)
            )

    def _eligible_clients_for_test(
        self, test_item: TestItem | None
    ) -> tuple[str, ...]:
        """Calcula a disponibilidade do mesmo arquivo no catálogo de cada cliente."""
        if test_item is None:
            return ()
        return tuple(
            client.key
            for client in self._configuration.clients
            if any(
                item.path == test_item.path
                for item in self._catalog_service.load_items_for_client(
                    client.key, client.version
                )
            )
        )

    def _select_client(self, client_key: str) -> None:
        """Atualiza as jornadas; a página limpa a seleção anterior."""
        if self.is_running:
            return
        if client_key == self._active_client.key:
            return
        client = self._clients.get(client_key)
        if client is None:
            return
        modules = self._load_modules(client)
        available_tests = self._load_tests(client)
        self._active_client = client
        self._plans.clear()
        self._selected_test = None
        self._parallel_tests.clear()
        self._count = 1
        self._run_all_clients = False
        self._eligible_client_keys = ()
        self._available_tests = available_tests
        if self._page is not None and self._page.winfo_exists():
            self._page.set_client_modules(client_key, modules)
            self._page.set_tests(self._available_tests)
            self._page.set_parallel_tests(())
            self._page.set_count(self._count)
            self._page.set_run_all_clients(False)
            self._page.set_eligible_clients(())

    def _select_module(self, module_prefix: str) -> None:
        """Alterna até duas jornadas para o mesmo cliente ativo."""
        active = self._execution_registry.running_records()
        if self._mode is not SentinelRunMode.JOURNEY or len(active) >= 2:
            return
        if any(record.snapshot.target == module_prefix for record in active):
            return
        if module_prefix in self._plans:
            del self._plans[module_prefix]
        elif len(self._plans) >= 2 - len(active):
            if self._page is not None and self._page.winfo_exists():
                self._page.show_selection_notice(
                    "Limite de vagas livres: remova uma jornada antes de trocar."
                )
            return
        else:
            plan: SentinelPlan = self._plan_service.build_plan(
                self._active_client.key,
                self._active_client.version,
                module_prefix,
            )
            self._plans[module_prefix] = plan
        if self._page is not None and self._page.winfo_exists():
            self._page.set_plans(tuple(self._plans.values()))

    def start(self) -> None:
        """Inicia a jornada selecionada e supervisiona sua saída na interface."""
        active = self._execution_registry.running_records()
        if len(active) >= 2 or (active and self._mode is not SentinelRunMode.JOURNEY):
            return
        if any(target in self._plans for target in (record.snapshot.target for record in active)):
            if self._page is not None and self._page.winfo_exists():
                self._page.show_selection_notice("Uma jornada em execução não pode ser iniciada novamente.")
            return
        if not self._can_start_execution():
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(self.is_running, "Outra execução está em andamento.")
                self._page.append_execution_log(
                    "Interrompa a execução do Pytest antes de iniciar a Sentinela."
                )
            return
        if self._ttl_days is None or not 1 <= self._ttl_days <= 365:
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(self.is_running, "Informe um TTL entre 1 e 365 dias.")
            return
        if self._mode is SentinelRunMode.JOURNEY and (
            not 1 <= len(self._plans) <= 2
            or any(not plan.can_start for plan in self._plans.values())
        ):
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(self.is_running, "Selecione uma ou duas jornadas válidas e distintas.")
            return
        if self._mode is SentinelRunMode.JOURNEY and self._count != 1:
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(
                    self.is_running, "A repetição está disponível somente para teste específico."
                )
            return
        selected_specific_tests = tuple(self._parallel_tests) or (
            (self._selected_test,) if self._selected_test is not None else ()
        )
        parallel_invalid = (
            not 1 <= len(selected_specific_tests) <= 2
            or any(test not in self._available_tests for test in selected_specific_tests)
            or len({test.path for test in selected_specific_tests}) != len(selected_specific_tests)
            or (len(selected_specific_tests) == 2 and self._count != 1)
        )
        if self._mode is SentinelRunMode.SPECIFIC_TEST and not self._run_all_clients and parallel_invalid:
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(self.is_running, "Selecione um ou dois testes distintos; lote não repete testes.")
            return
        if self._mode is SentinelRunMode.SPECIFIC_TEST and self._run_all_clients and self._selected_test is None:
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(self.is_running, "Selecione um teste específico.")
            return
        if self._mode is SentinelRunMode.JOURNEY and self._run_all_clients:
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(
                    self.is_running,
                    "Modo multi-cliente disponível somente para teste específico.",
                )
            return
        if self._mode is SentinelRunMode.SPECIFIC_TEST and self._plans:
            self._plans.clear()
            if self._page is not None and self._page.winfo_exists():
                self._page.set_plans(())
        if self._mode is SentinelRunMode.SPECIFIC_TEST and self._selected_test is None:
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(self.is_running, "Selecione um teste específico.")
            return
        if self._mode is SentinelRunMode.SPECIFIC_TEST and not self._run_all_clients:
            # Um cálculo por teste (varre o catálogo de todos os clientes); lista vazia
            # já implica cliente ativo ausente.
            if any(
                self._active_client.key not in self._eligible_clients_for_test(item)
                for item in selected_specific_tests
            ):
                if self._page is not None and self._page.winfo_exists():
                    self._page.set_running(self.is_running, "Teste não disponível no cliente ativo.")
                return
        if self._mode is SentinelRunMode.SPECIFIC_TEST and self._run_all_clients:
            if not self._eligible_client_keys:
                if self._page is not None and self._page.winfo_exists():
                    self._page.set_running(self.is_running, "Nenhum cliente compatível com o teste.")
                return
        command_service = SentinelCommandService()
        try:
            if self._mode is SentinelRunMode.JOURNEY:
                plans = tuple(self._plans.values())
                if len(plans) == 1:
                    commands = (
                        command_service.build(
                            self._active_client.key, plans[0], self._ttl_days
                        ),
                    )
                else:
                    commands = command_service.build_journey_batch(
                        self._active_client.key, plans, self._ttl_days
                    )
                targets = tuple(plan.module_prefix for plan in plans)
            else:
                if self._run_all_clients:
                    assert self._selected_test is not None
                    items_by_client = {
                        client.key: self._catalog_service.load_items_for_client(
                            client.key, client.version
                        )
                        for client in self._configuration.clients
                    }
                    command = command_service.build_all_clients_specific_test(
                        self._selected_test,
                        self._eligible_client_keys,
                        items_by_client,
                        self._count,
                        self._ttl_days,
                    )
                    commands = (command,)
                    targets = (self._selected_test.path,)
                else:
                    parallel_tests = selected_specific_tests
                    if len(parallel_tests) == 2:
                        commands = command_service.build_specific_test_batch(
                            self._active_client.key,
                            parallel_tests,
                            self._available_tests,
                            self._ttl_days,
                        )
                    else:
                        test_item = parallel_tests[0]
                        commands = (
                            command_service.build_specific_test(
                                self._active_client.key,
                                test_item,
                                self._available_tests,
                                count=self._count,
                                ttl_days=self._ttl_days,
                            ),
                        )
                    targets = tuple(item.path for item in parallel_tests)
        except (OSError, ValueError, RuntimeError) as error:
            if self._page is not None and self._page.winfo_exists():
                self._page.append_execution_log(f"Falha na validação do lote: {error}")
                self._page.set_running(self.is_running, "Falha na validação da execução.")
            return

        records = self._build_records(targets)
        if len(self._execution_registry.running_records()) + len(records) > 2:
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(self.is_running, "O limite de duas execuções já está ocupado.")
            return
        try:
            self._execution_registry.register_batch(records)
        except ValueError as error:
            if self._page is not None and self._page.winfo_exists():
                self._page.append_execution_log(f"Falha ao reservar execuções: {error}")
                self._page.set_running(self.is_running, "Falha ao preparar as execuções.")
            return
        self._run_artifact_ids.update(record.execution_id for record in records)
        self._selected_execution_id = records[0].execution_id
        for record in records:
            client_label = (
                "todos" if self._run_all_clients else record.snapshot.client_key
            )
            record.output.append(
                f"Iniciando cliente {client_label}: "
                f"{record.snapshot.target} · ID {record.execution_id}"
            )
        self._sync_execution_panel()
        try:
            for record, command in zip(records, commands, strict=True):
                service = record.supervisor
                assert isinstance(service, SentinelExecutionService)
                record.events = service.start_command(command, record.execution_id)
                if service.execution_id != record.execution_id:
                    raise RuntimeError("A Sentinela alterou o execution_id solicitado.")
                record.state = ExecutionState.RUNNING
        except Exception as error:
            self._terminalize_unstarted(records)
            for record in records:
                record.output.append(f"Falha ao iniciar: {error}")
            self._stop_records(
                tuple(record for record in records if record.state is ExecutionState.RUNNING)
            )
            if self._page is not None and self._page.winfo_exists():
                self._page.set_running(
                    self.is_running,
                    "Falha parcial ao iniciar; aguardando encerramento seguro."
                    if self.is_running
                    else "Falha ao iniciar a execução.",
                )
            self._sync_execution_panel()
            if self.is_running:
                self._schedule_poll()
            elif self._host is not None and self._host.winfo_exists():
                self._schedule_poll()
            return

        self._last_status = "Sentinela em execução…"
        if self._page is not None and self._page.winfo_exists():
            self._page.set_running(True, "Sentinela em execução…")
            self._page.set_plans(())
        self._plans.clear()
        self._sync_execution_panel()
        self._schedule_poll()

    def _build_records(self, targets: tuple[str, ...]) -> list[ExecutionRecord]:
        """Cria snapshots imutáveis e supervisores isolados sem alterar o registro."""
        records: list[ExecutionRecord] = []
        for target in targets:
            snapshot = ExecutionSnapshot(
                client_key=None if self._run_all_clients else self._active_client.key,
                mode=self._mode.value,
                target=target,
                count=self._count,
                ttl_days=self._ttl_days,
                options=(
                    targets
                    if self._mode is SentinelRunMode.JOURNEY
                    else self._eligible_client_keys
                    if self._run_all_clients
                    else ()
                ),
            )
            records.append(
                ExecutionRecord(
                    execution_id=uuid4().hex,
                    snapshot=snapshot,
                    events=queue.Queue(),
                    supervisor=SentinelExecutionService(),
                    state=ExecutionState.STARTING,
                )
            )
        return records

    @staticmethod
    def _terminalize_unstarted(records: list[ExecutionRecord]) -> None:
        """Marca como falhos os registros sem processo após início parcial inválido."""
        now = datetime.now(timezone.utc)
        for record in records:
            if record.state is ExecutionState.STARTING:
                record.state = ExecutionState.FAILED
                record.finished_at = now

    def stop(self, execution_id: str | None = None) -> None:
        """Para uma execução identificada ou todas as ativas ao fechar a janela."""
        if execution_id is None:
            records = self._execution_registry.running_records()
        else:
            owned = self._execution_registry.get(execution_id)
            records = (
                (owned,)
                if owned is not None and owned.state in (
                    ExecutionState.STARTING,
                    ExecutionState.RUNNING,
                    ExecutionState.PAUSE_REQUESTED,
                    ExecutionState.PAUSED_BETWEEN_TESTS,
                    ExecutionState.STOPPING,
                )
                else ()
            )
        records = tuple(
            record
            for record in records
            if record.execution_id not in self._stop_requested_ids
        )
        if not records:
            return
        self._stop_records(records)

    def request_stop(self) -> None:
        """Pede ao usuário quais execuções ativas deseja parar."""
        records = tuple(
            record for record in self._execution_registry.running_records()
            if record.execution_id not in self._stop_requested_ids
            and record.state is not ExecutionState.STOPPING
        )
        page = self._page
        if not records or page is None or not page.winfo_exists():
            return
        records = tuple(sorted(records, key=lambda record: record.execution_id != self._selected_execution_id))
        choice = page.choose_stop_targets(
            tuple((record.execution_id, record.snapshot.target) for record in records)
        )
        if choice is None:
            return
        if choice == "all":
            self.stop()
        else:
            self.stop(choice)

    def _stop_records(
        self, records: tuple[ExecutionRecord, ...] | list[ExecutionRecord]
    ) -> None:
        """Solicita parada apenas aos supervisors das identidades recebidas."""
        if not records:
            return
        for record in records:
            if record.execution_id in self._stop_requested_ids:
                continue
            self._write_control_command(record, "stop")
            self._stop_requested_ids.add(record.execution_id)
            service = record.supervisor
            if isinstance(service, SentinelExecutionService):
                completed = threading.Event()
                self._stop_completion_events[record.execution_id] = completed
                thread = threading.Thread(
                    target=self._stop_one,
                    args=(service, record.execution_id, completed),
                    name=f"sentinel-stop-{record.execution_id}",
                    daemon=True,
                )
                self._stop_threads[record.execution_id] = thread
                record.state = ExecutionState.STOPPING
                thread.start()
            else:
                record.state = ExecutionState.FAILED
                record.finished_at = datetime.now(timezone.utc)
            if self._host is None:
                self._stop_completion_events.pop(record.execution_id, None)
            record.output.append(
                f"Solicitado encerramento da execução {record.execution_id}."
            )
        total_stopping = sum(
            record.state is ExecutionState.STOPPING
            for record in self._execution_registry.running_records()
        )
        self._last_status = f"Interrompendo {total_stopping} execução(ões)…"
        if self._page is not None and self._page.winfo_exists():
            self._page.set_running(True, self._last_status)
        self._sync_execution_panel()
        if self._host is not None and self._host.winfo_exists():
            if self._poll_after_id is None:
                self._schedule_poll()

    def toggle_pause(self) -> None:
        """Pausa a sequência selecionada ou continua após a fronteira segura."""
        execution_id = self._selected_execution_id
        record = self._execution_registry.get(execution_id or "")
        if record is None or record.state is ExecutionState.STOPPING:
            return
        if record.state is ExecutionState.RUNNING:
            if not self._write_control_command(record, "pause"):
                return
            record.state = ExecutionState.PAUSE_REQUESTED
            record.output.append(
                "Pausa solicitada; aguardando o teste atual e suas retentativas terminarem."
            )
        elif record.state is ExecutionState.PAUSED_BETWEEN_TESTS:
            if not self._write_control_command(record, "resume"):
                return
            record.state = ExecutionState.RUNNING
            record.output.append("Continuação solicitada.")
        elif record.state is ExecutionState.PAUSE_REQUESTED:
            if not self._write_control_command(record, "resume"):
                return
            record.state = ExecutionState.RUNNING
            record.output.append("Pausa cancelada antes da fronteira segura.")
        else:
            return
        self._sync_execution_panel()

    def _write_control_command(self, record: ExecutionRecord, command: str) -> bool:
        """Escreve comando somente após validar a pasta exclusiva do registro."""
        artifacts = self._artifact_service.locate(
            record.output, record.execution_id
        )
        if artifacts.folder_path is None:
            if command in {"pause", "resume"}:
                record.output.append(
                    "Controle indisponível: a pasta exclusiva do run ainda não foi validada."
                )
                self._sync_execution_panel()
                return False
            return True
        try:
            self._control_service.write_command(
                artifacts.folder_path, record.execution_id, command
            )
        except (OSError, ValueError, RuntimeError) as error:
            record.output.append(f"Não foi possível enviar {command}: {error}")
            self._sync_execution_panel()
            return False
        return True

    @staticmethod
    def _stop_one(
        service: SentinelExecutionService,
        execution_id: str,
        completed: threading.Event,
    ) -> None:
        """Executa stop num thread dedicado e sinaliza conclusão ao fechamento."""
        try:
            service.stop()
        except Exception:
            _LOGGER.exception("Falha ao parar a execução Sentinela %s.", execution_id)
        finally:
            completed.set()

    def wait_for_stop(self, timeout: float = 10.0) -> bool:
        """Aguarda por tempo limitado as árvores conhecidas chegarem ao terminal."""
        deadline = time.monotonic() + timeout
        executions = tuple(
            (execution_id, event)
            for execution_id, event in self._stop_completion_events.items()
        )
        for execution_id, completed in executions:
            if not completed.wait(max(0.0, deadline - time.monotonic())):
                self._ensure_stop_event_finalized(execution_id)
                return False
        for execution_id, _completed in executions:
            thread = self._stop_threads.get(execution_id)
            if thread is None:
                continue
            thread.join(max(0.0, deadline - time.monotonic()))
        stopped = all(
            (thread := self._stop_threads.get(execution_id)) is None
            or not thread.is_alive()
            for execution_id, _completed in executions
        )
        if stopped:
            for execution_id, _completed in executions:
                self._ensure_stop_event_finalized(execution_id)
        return stopped and not self.is_running

    def _ensure_stop_event_finalized(self, execution_id: str) -> None:
        """Finaliza só a identidade consultada caso o fechamento alcance o prazo."""
        record = self._execution_registry.get(execution_id)
        service = record.supervisor if record is not None else None
        if (
            record is None
            or not isinstance(service, SentinelExecutionService)
            or record.state not in (ExecutionState.RUNNING, ExecutionState.STOPPING)
        ):
            return
        try:
            return_code = service.wait(0)
        except subprocess.TimeoutExpired:
            return
        if return_code is None:
            return
        while True:
            try:
                event = record.events.get_nowait()
            except queue.Empty:
                break
            if not event_belongs_to_execution(event, execution_id):
                continue
            if event.event_type is not ExecutionEventType.PROCESS_EXITED:
                record.output.append(event.message)
        event = ExecutionEvent(
            ExecutionEventType.PROCESS_EXITED,
            (
                ExecutionEventLevel.ERROR
                if service.last_stop_mode == "forced"
                else ExecutionEventLevel.INFO
            ),
            "Processo encerrado.",
            return_code=return_code,
            execution_id=execution_id,
        )
        self._finalize_record(record, event)

    def stop_all_and_wait(self, timeout: float = 10.0) -> bool:
        """Solicita parada de todos os processos próprios e aguarda até o limite."""
        self.stop()
        return self.wait_for_stop(timeout)

    def _schedule_poll(self) -> None:
        if self._poll_after_id is None and self._host is not None and self._host.winfo_exists():
            self._poll_after_id = self._host.after(100, self._poll_events)

    def _poll_events(self) -> None:
        """Consome saída e estado final sem bloquear o loop do Tk."""
        self._poll_after_id = None
        records = self._execution_registry.running_records()
        now = time.monotonic()
        if records and now - self._last_metrics_sample_at >= 1.0:
            self._last_metrics_sample_at = now
            for record in records:
                service = record.supervisor
                if not isinstance(service, SentinelExecutionService):
                    continue
                metrics = service.supervisor.sample_metrics()
                if metrics is not None:
                    record.metrics = metrics
        if not records:
            if not self._run_artifact_ids:
                self._last_status = getattr(
                    self, "_last_status", "Execução concluída."
                )
            else:
                batch_records = tuple(
                    record
                    for record in self._execution_registry.all_records()
                    if record.execution_id in self._run_artifact_ids
                    and record.state in (
                        ExecutionState.SUCCEEDED,
                        ExecutionState.FAILED,
                        ExecutionState.INTERRUPTED,
                    )
                )
                successful = sum(
                    record.state is ExecutionState.SUCCEEDED
                    for record in batch_records
                )
                failed = sum(
                    record.state is ExecutionState.FAILED for record in batch_records
                )
                interrupted = sum(
                    record.state is ExecutionState.INTERRUPTED
                    for record in batch_records
                )
                if successful and not failed and not interrupted:
                    self._last_status = (
                        f"{successful} jornada(s) concluída(s) com sucesso."
                    )
                elif failed or interrupted:
                    self._last_status = (
                        f"Execuções encerradas: {successful} sucesso(s), {failed} falha(s), "
                        f"{interrupted} interrompida(s)."
                    )
            page = self._page
            if page is not None and page.winfo_exists() and not self._run_artifact_ids:
                page.set_running(False, None if self._plans else self._last_status)
            if self._run_artifact_ids:
                self._finish_batch(
                    page if page is not None and page.winfo_exists() else None
                )
            return
        page = self._page
        page = page if page is not None and page.winfo_exists() else None
        for record in records:
            for _ in range(250):
                try:
                    event = record.events.get_nowait()
                except queue.Empty:
                    break
                if not event_belongs_to_execution(event, record.execution_id):
                    continue
                if event.event_type is ExecutionEventType.PROCESS_EXITED:
                    stop_thread = self._stop_threads.get(record.execution_id)
                    if stop_thread is not None and stop_thread.is_alive():
                        # stop() is normally fast; defer finalization briefly so the
                        # supervisor can record whether Ctrl+Break or force was needed.
                        if record.execution_id not in self._exit_requeue_pending:
                            self._exit_requeue_pending.add(record.execution_id)
                            threading.Timer(
                                0.02,
                                self._requeue_exit_event,
                                args=(record, event),
                            ).start()
                        break
                    self._finalize_record(record, event)
                    continue
                if event.event_type in (
                    ExecutionEventType.STDOUT,
                    ExecutionEventType.STDERR,
                ) and self._consume_control_event(record, event.message):
                    continue
                record.output.append(event.message)
            stop_completed = self._stop_completion_events.get(record.execution_id)
            stop_thread = self._stop_threads.get(record.execution_id)
            if (
                record.state is ExecutionState.STOPPING
                and record.events.empty()
                and stop_completed is not None
                and stop_completed.is_set()
                and stop_thread is not None
                and not stop_thread.is_alive()
                and isinstance(record.supervisor, SentinelExecutionService)
            ):
                try:
                    return_code = record.supervisor.wait(0)
                except subprocess.TimeoutExpired:
                    continue
                if return_code is None:
                    continue
                self._finalize_record(
                    record,
                    ExecutionEvent(
                        ExecutionEventType.PROCESS_EXITED,
                        level=(
                            ExecutionEventLevel.ERROR
                            if record.supervisor.last_stop_mode == "forced"
                            else ExecutionEventLevel.INFO
                        ),
                        message="Processo encerrado pelo cancelamento.",
                        return_code=return_code,
                        execution_id=record.execution_id,
                    ),
                )
        remaining_records = self._execution_registry.running_records()
        remaining = len(remaining_records)
        if page is not None:
            stopping = sum(
                record.state is ExecutionState.STOPPING
                for record in remaining_records
            )
            if stopping:
                status = f"Interrompendo {stopping} execução(ões)…"
            elif self._plans and remaining < 2:
                status = None
            else:
                status = (
                    f"{remaining} jornada(s) em execução…"
                    if remaining
                    else getattr(self, "_last_status", "Execução concluída.")
                )
            page.set_running(bool(remaining), status)
        if not self.is_running:
            self._finish_batch(page)
        if self.is_running:
            self._schedule_poll()
        self._sync_execution_panel()

    def _finish_batch(self, page: SentinelPage | None) -> None:
        """Agrega os estados terminais do lote atual sem misturar histórico antigo."""
        batch_records = tuple(
            record
            for record in self._execution_registry.all_records()
            if record.execution_id in self._run_artifact_ids
        )
        successful = sum(
            record.state is ExecutionState.SUCCEEDED for record in batch_records
        )
        failed = sum(
            record.state is ExecutionState.FAILED for record in batch_records
        )
        interrupted = sum(
            record.state is ExecutionState.INTERRUPTED for record in batch_records
        )
        if successful and not failed and not interrupted:
            self._last_status = f"{successful} execução(ões) concluída(s) com sucesso."
        elif failed or interrupted:
            self._last_status = (
                f"Execuções encerradas: {successful} sucesso(s), {failed} falha(s), "
                f"{interrupted} interrompida(s)."
            )
        if page is not None:
            if self._plans:
                page.set_plans(tuple(self._plans.values()))
            page.set_running(False, None if self._plans else self._last_status)
        self._run_artifact_ids.clear()

    def _finalize_record(self, record: ExecutionRecord, event: ExecutionEvent) -> None:
        """Aplica estado e artefatos exclusivamente ao registro do evento final."""
        self._stop_threads.pop(record.execution_id, None)
        self._exit_requeue_pending.discard(record.execution_id)
        try:
            self._control_service.remove_command(record.execution_id)
        except OSError:
            _LOGGER.warning(
                "Não foi possível remover o controle da execução %s.",
                record.execution_id,
                exc_info=True,
            )
        service = record.supervisor
        if isinstance(service, SentinelExecutionService):
            final_metrics = service.supervisor.sample_metrics()
            if final_metrics is not None:
                record.metrics = final_metrics
        stop_requested = record.execution_id in self._stop_requested_ids
        stop_mode = (
            service.last_stop_mode
            if isinstance(service, SentinelExecutionService)
            else None
        )
        artifacts = self._artifact_service.locate(record.output, record.execution_id)
        self._artifacts_by_execution[record.execution_id] = artifacts
        self._artifact_scans[record.execution_id] = _ArtifactScan(
            scanned_lines=len(record.output),
            listed_at=time.monotonic(),
            artifacts=artifacts,
            announced=True,
        )
        report_failed = self._artifact_service.report_has_failures(artifacts.report_path)
        execution_failed = event.return_code != 0 or report_failed is not False
        if stop_requested and stop_mode == "already_completed" and not execution_failed:
            status = "Execução concluída antes do pedido de parada."
        elif stop_requested and stop_mode == "graceful":
            status = "Execução interrompida graciosamente."
        elif stop_requested and stop_mode == "forced":
            status = "Execução interrompida à força."
        elif report_failed:
            status = "Execução terminou com teste(s) falho(s)."
        elif event.return_code == 0 and report_failed is None:
            status = "Processo encerrado, mas o resultado não pôde ser confirmado pelo relatório."
        elif event.return_code == 0:
            status = "Execução concluída com sucesso."
        else:
            status = f"Execução falhou (código {event.return_code})."
        record.state = (
            ExecutionState.INTERRUPTED
            if stop_requested and stop_mode in ("graceful", "forced")
            else ExecutionState.FAILED
            if execution_failed
            else ExecutionState.SUCCEEDED
            if event.return_code == 0 or stop_mode == "already_completed"
            else ExecutionState.FAILED
        )
        record.finished_at = datetime.now(timezone.utc)
        record.artifact_paths = [
            path
            for path in (
                artifacts.folder_path,
                artifacts.report_path,
                *artifacts.trace_paths,
            )
            if path is not None
        ]
        self._stop_requested_ids.discard(record.execution_id)
        self._last_status = status
        record.output.append(status)
        if stop_requested and isinstance(service, SentinelExecutionService):
            if service.last_stop_detail:
                record.output.append(service.last_stop_detail)
        stop_completed = self._stop_completion_events.pop(record.execution_id, None)
        if stop_completed is not None:
            stop_completed.set()
        self._stop_threads.pop(record.execution_id, None)
        self._sync_execution_panel()

    def _requeue_exit_event(
        self, record: ExecutionRecord, event: ExecutionEvent
    ) -> None:
        """Recoloca o evento final após o supervisor concluir a rotina de stop."""
        if record.state is not ExecutionState.STOPPING:
            return
        self._exit_requeue_pending.discard(record.execution_id)
        record.events.put(event)
        # Executado por Timer: o polling já agendado na thread principal
        # consome a fila. Até winfo_exists() acessaria Tcl fora dessa thread.

    def artifacts_for(self, execution_id: str) -> SentinelRunArtifacts | None:
        """Obtém artefatos somente do registro que possui a identidade pedida."""
        return self._artifacts_by_execution.get(execution_id)

    def _select_execution(self, execution_id: str) -> None:
        """Seleciona a identidade que controla logs e artefatos apresentados."""
        if (
            self._execution_registry.get(execution_id) is None
            and not any(run.execution_id == execution_id for run in self._history_runs)
        ):
            return
        self._selected_execution_id = execution_id
        self._sync_execution_panel()

    def _consume_control_event(self, record: ExecutionRecord, message: str) -> bool:
        """Aplica marcadores de estado somente quando a identidade confere."""
        if not message.startswith(_CONTROL_EVENT_PREFIX):
            return False
        raw_id_and_state = message[len(_CONTROL_EVENT_PREFIX) :]
        execution_id, separator, raw_state = raw_id_and_state.partition(":")
        if not separator or execution_id != record.execution_id:
            return True
        try:
            state = ExecutionState(raw_state)
        except ValueError:
            return True
        if record.state is ExecutionState.STOPPING:
            return True
        if state is ExecutionState.PAUSED_BETWEEN_TESTS:
            record.state = state
            record.output.append("Execução pausada entre testes.")
            self._sync_execution_panel()
        elif state is ExecutionState.RUNNING:
            record.state = state
            record.output.append("Execução continuada.")
            self._sync_execution_panel()
        return True

    def _sync_execution_panel(self) -> None:
        """Atualiza a página a partir dos registros, sem agregar irmãos."""
        page = self._page
        if page is None or not page.winfo_exists():
            return
        self._refresh_history_if_removed()
        all_records = self._execution_registry.all_records()
        running_ids = {
            record.execution_id for record in self._execution_registry.running_records()
        }
        running_records = tuple(
            record for record in all_records if record.execution_id in running_ids
        )
        finished_slots = max(0, MAX_HISTORY_RUNS - len(running_records))
        finished_records = tuple(
            record
            for record in all_records
            if record.execution_id not in running_ids
        )
        recent_finished = finished_records[-finished_slots:] if finished_slots else ()
        records = tuple(
            sorted(
                (*running_records, *recent_finished),
                key=lambda record: record.started_at,
            )
        )
        history_slots = max(0, MAX_HISTORY_RUNS - len(records))
        # A saída vai por referência: a página só lê as linhas que ainda não exibiu.
        executions = tuple(
            (
                record.execution_id,
                record.snapshot.target,
                record.state.value,
                record.output,
                ("Última amostra · " if record.finished_at is not None else "")
                + self._format_metrics(record.metrics),
            )
            for record in records
        )
        active_ids = {record.execution_id for record in records}
        historical = tuple(
            (
                run.execution_id,
                run.target,
                f"Histórico · {run.state}",
                self._history_output_by_id[run.execution_id],
                f"Iniciado em {run.started_at:%d/%m/%Y %H:%M}",
                True,
            )
            for run in self._history_runs
            if run.execution_id not in active_ids
        )[:history_slots]
        executions = executions + historical
        visible_ids = {record.execution_id for record in records}
        visible_history_ids = {run.execution_id for run in self._history_runs[:history_slots]}
        if (
            self._selected_execution_id not in visible_ids
            and self._selected_execution_id not in visible_history_ids
        ):
            self._selected_execution_id = (
                records[-1].execution_id
                if records
                else self._history_runs[0].execution_id
                if history_slots and self._history_runs
                else None
            )
        selected = self._execution_registry.get(self._selected_execution_id or "")
        selected_history = next(
            (run for run in self._history_runs if run.execution_id == self._selected_execution_id),
            None,
        )
        selected_artifacts = (
            self._locate_artifacts_incrementally(selected)
            if selected is not None
            else SentinelRunArtifacts(
                selected_history.report_path,
                selected_history.folder_path,
                selected_history.trace_paths,
            )
            if selected_history is not None
            else SentinelRunArtifacts(None, None)
        )
        page.set_execution_records(
            executions,
            self._selected_execution_id,
            can_control_selected=(
                selected is not None and selected_artifacts.folder_path is not None
            ),
        )
        page.set_capacity(
            2 - len(running_records),
            {record.snapshot.target for record in running_records},
        )
        self._artifacts = (
            self._artifacts_by_execution.get(selected.execution_id)
            if selected is not None
            else None
        ) or SentinelRunArtifacts(None, None)
        if selected_artifacts.folder_path is not None:
            self._artifacts = selected_artifacts
        page.set_artifacts(self._artifacts)

    def _locate_artifacts_incrementally(
        self, record: ExecutionRecord
    ) -> SentinelRunArtifacts:
        """Evita reler toda a saída e o disco a cada tick do polling.

        Relocaliza só quando chega linha que anuncia pasta/relatório; com a pasta
        já validada, apenas re-lista os traces a cada ``_TRACE_REFRESH_SECONDS``.
        """
        output = record.output
        now = time.monotonic()
        scan = self._artifact_scans.get(record.execution_id)
        new_mention = any(
            self._artifact_service.mentions_artifacts(line)
            for line in output[scan.scanned_lines if scan is not None else 0:]
        )
        if scan is not None and not new_mention:
            scan.scanned_lines = len(output)
            folder = scan.artifacts.folder_path
            if folder is not None and not folder.is_dir():
                scan.artifacts = SentinelRunArtifacts(None, None)
                self._artifacts_by_execution.pop(record.execution_id, None)
                return scan.artifacts
            report = scan.artifacts.report_path
            if report is not None and not report.is_file():
                scan.artifacts = replace(scan.artifacts, report_path=None)
            if not scan.announced or now - scan.listed_at < _TRACE_REFRESH_SECONDS:
                return scan.artifacts
            if scan.artifacts.folder_path is not None:
                scan.artifacts = replace(
                    scan.artifacts,
                    trace_paths=self._artifact_service.list_traces(
                        scan.artifacts.folder_path
                    ),
                )
                scan.listed_at = now
                return scan.artifacts
            # Pasta anunciada mas ainda não validada: tenta de novo abaixo.
        artifacts = self._artifact_service.locate(output, record.execution_id)
        self._artifact_scans[record.execution_id] = _ArtifactScan(
            scanned_lines=len(output),
            listed_at=now,
            artifacts=artifacts,
            announced=new_mention or (scan is not None and scan.announced),
        )
        return artifacts

    @staticmethod
    def _format_metrics(metrics: ProcessMetrics | None) -> str:
        """Formata a última amostra agregada do processo Sentinela selecionado."""
        if metrics is None:
            return "Recursos: indisponível"
        cpu = (
            f"CPU {metrics.cpu_percent:.1f}%"
            if metrics.cpu_percent is not None
            else "CPU coletando…"
        )
        memory_mib = metrics.working_set_bytes / (1024 * 1024)
        return (
            f"Recursos do processo: {cpu} · RAM {memory_mib:.0f} MiB · "
            f"processos de navegador {metrics.browser_count} · processos {metrics.process_count}"
        )

    def open_report(self) -> None:
        """Abre o HTML associado à execução selecionada."""
        artifacts = self._artifacts_for_active_selection()
        path = artifacts.report_path if artifacts is not None else None
        if path is None:
            return
        try:
            self._artifact_service.open_report(path)
        except (OSError, ValueError) as error:
            self._log_artifact_error(error)

    def open_folder(self) -> None:
        """Abre a pasta associada à execução selecionada."""
        artifacts = self._artifacts_for_active_selection()
        path = artifacts.folder_path if artifacts is not None else None
        if path is None:
            return
        try:
            self._artifact_service.open_folder(path)
        except (OSError, ValueError) as error:
            self._log_artifact_error(error)

    def open_trace(self, trace_path: Path) -> None:
        """Abre somente trace pertencente à execução selecionada."""
        artifacts = self._artifacts_for_active_selection()
        if (
            artifacts is None
            or trace_path not in artifacts.trace_paths
            or artifacts.folder_path is None
        ):
            return
        try:
            self._artifact_service.open_trace(
                trace_path, artifacts.folder_path
            )
        except (OSError, ValueError) as error:
            self._log_artifact_error(error)

    def _log_artifact_error(self, error: Exception) -> None:
        if self._page is not None and self._page.winfo_exists():
            self._page.append_execution_log(f"Não foi possível abrir o artefato: {error}")

    def _artifacts_for_active_selection(self) -> SentinelRunArtifacts | None:
        """Retorna artefatos pertencentes somente à execução selecionada."""
        record = self._execution_registry.get(self._selected_execution_id or "")
        if record is not None:
            return self._artifact_service.locate(record.output, record.execution_id)
        run = next(
            (run for run in self._history_runs if run.execution_id == self._selected_execution_id),
            None,
        )
        if run is None:
            return None
        artifacts = self._artifact_service.locate(
            (f"Run salvo em [{run.execution_id}]: {run.folder_path}",),
            run.execution_id,
        )
        if self._page is not None and self._page.winfo_exists():
            self._page.set_artifacts(artifacts)
        return artifacts
