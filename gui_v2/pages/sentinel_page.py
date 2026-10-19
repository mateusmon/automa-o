"""Página de seleção de jornadas da Sentinela."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from tkinter import END, StringVar, messagebox
import unicodedata

import customtkinter as ctk
from gui_v2.components.smart_scrollable_frame import SmartScrollableFrame

from gui_v2.components.client_picker import ClientPicker
from gui_v2.components.page_header import PageHeader
from gui_v2.components.test_picker import TestPicker
from gui_v2.services.sentinel_artifact_service import SentinelRunArtifacts
from gui_v2.services.sentinel_plan_service import SentinelModule, SentinelPlan
from gui_v2.models.test_item import TestItem
from gui_v2.services.sentinel_command_service import SentinelRunMode
from gui_v2.theme import COLORS


@dataclass(slots=True)
class _ModuleButtons:
    """Botões de uma jornada visível e o estado visual aplicado."""

    module_button: ctk.CTkButton
    expand_button: ctk.CTkButton | None
    title: str
    applied: tuple[bool, str] = (False, "normal")


def _client_label_sort_key(label: str) -> str:
    """Normaliza rótulos para ordenação alfabética sem diferenciar acentos."""
    decomposed = unicodedata.normalize("NFD", label.casefold())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


class SentinelPage(SmartScrollableFrame):
    """Apresenta jornadas disponíveis e permite selecionar módulo/submódulo."""

    MAX_LOG_LINES = 10_000

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        clients: Mapping[str, str],
        active_client_key: str,
        modules: Sequence[SentinelModule],
        tests: Sequence[TestItem],
        on_mode_selected: Callable[[SentinelRunMode], None],
        on_test_selected: Callable[[str], None],
        on_count_selected: Callable[[int], None],
        on_all_clients_selected: Callable[[bool], None],
        retry_limit: int,
        on_client_selected: Callable[[str], None],
        on_module_selected: Callable[[str], None],
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        on_pause: Callable[[], None],
        on_open_report: Callable[[], None],
        on_open_folder: Callable[[], None],
        on_open_trace: Callable[[Path], None],
        on_execution_selected: Callable[[str], None],
        on_test_toggled: Callable[[str], None],
        on_test_removed: Callable[[str], None],
        on_toggle_logs: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color=COLORS["page"], corner_radius=0)
        self._parent_canvas.configure(yscrollincrement=5)
        self._on_client_selected = on_client_selected
        self._on_mode_selected = on_mode_selected
        self._on_test_selected = on_test_selected
        self._on_count_selected = on_count_selected
        self._on_all_clients_selected = on_all_clients_selected
        self._retry_limit = retry_limit
        self._count = 1
        self._run_all_clients = False
        self._eligible_client_labels: tuple[str, ...] = ()
        self._on_module_selected = on_module_selected
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_pause = on_pause
        self._on_open_report = on_open_report
        self._on_open_folder = on_open_folder
        self._on_open_trace = on_open_trace
        self._on_execution_selected = on_execution_selected
        self._on_test_toggled = on_test_toggled
        self._on_test_removed = on_test_removed
        self._on_toggle_logs = on_toggle_logs
        self._running = False
        self._free_slots = 2
        self._active_targets: set[str] = set()
        self._plans: tuple[SentinelPlan, ...] = ()
        self._artifacts = SentinelRunArtifacts(None, None)
        self._trace_paths: dict[str, Path] = {}
        self._execution_ids_by_label: dict[str, str] = {}
        self._execution_labels_cache: tuple[str, ...] = ()
        # (execução exibida, linhas já exibidas); None após escrita avulsa no log.
        self._execution_log_key: tuple[str | None, int] | None = None
        self._execution_selection_cache: str | None = None
        self._execution_state_cache: str | None = None
        self._modules: tuple[SentinelModule, ...] = ()
        self._tests: tuple[TestItem, ...] = tuple(tests)
        self._selected_test: TestItem | None = None
        self._parallel_tests: tuple[TestItem, ...] = ()
        self._mode = SentinelRunMode.JOURNEY
        self._selected_modules: set[str] = set()
        self._expanded_modules: set[str] = set()
        self._module_buttons: dict[str, _ModuleButtons] = {}
        self._module_render_key: tuple[tuple[SentinelModule, ...], frozenset[str]] | None = None

        self.grid_columnconfigure(0, weight=1)
        PageHeader(
            self,
            "Sentinela",
            "Selecione um cliente, uma jornada ou um teste específico",
        ).grid(row=0, column=0, sticky="ew", padx=32, pady=(26, 16))

        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=1, column=0, sticky="ew", padx=32)
        card.grid_columnconfigure((0, 1), weight=1, uniform="sentinel_columns")
        card.grid_rowconfigure(2, weight=1, minsize=200)

        controls = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )
        controls.grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))
        ctk.CTkLabel(
            controls,
            text="Cliente",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", padx=(0, 12), pady=10)
        self._client_picker = ClientPicker(
            controls,
            clients=clients,
            active_client_key=active_client_key,
            on_selected=on_client_selected,
            width=240,
        )
        self._client_picker.grid_propagate(False)
        self._client_picker.pack(side="left", pady=10)
        ctk.CTkLabel(
            controls,
            text="Modo",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", padx=(24, 12), pady=10)
        self._mode_picker = ClientPicker(
            controls,
            clients={mode.value: mode.value for mode in SentinelRunMode},
            active_client_key=self._mode.value,
            on_selected=self._mode_changed,
            width=180,
            searchable=False,
        )
        self._mode_picker.grid_propagate(False)
        self._mode_picker.pack(side="left", pady=10)
        self._module_title = ctk.CTkLabel(
            card,
            text="Jornadas disponíveis · até duas",
            anchor="w",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self._module_title.grid(row=1, column=0, sticky="ew", padx=(24, 12), pady=(8, 10))
        self._plan_title = ctk.CTkLabel(
            card,
            text="Prévia do plano",
            anchor="w",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self._plan_title.grid(row=1, column=1, sticky="ew", padx=(12, 24), pady=(8, 10))
        self._module_list = SmartScrollableFrame(
            card,
            fg_color=COLORS["surface_alt"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        self._module_list.grid(row=2, column=0, sticky="nsew", padx=(24, 12), pady=(0, 12))
        self._module_list.grid_columnconfigure(0, weight=1)
        self._plan_content = ctk.CTkTextbox(
            card,
            fg_color=COLORS["surface_alt"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            wrap="word",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=12),
            state="disabled",
        )
        self._plan_content.grid(
            row=2, column=1, sticky="nsew", padx=(12, 24), pady=(0, 12)
        )
        self.protect_textbox(self._plan_content)
        self._specific_test_frame = SmartScrollableFrame(
            card,
            fg_color=COLORS["surface_alt"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        self._specific_test_frame.grid_columnconfigure(
            (0, 1), weight=1, uniform="specific_test"
        )
        self._test_pickers_frame = ctk.CTkFrame(
            self._specific_test_frame, fg_color="transparent"
        )
        self._test_pickers_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(14, 8)
        )
        self._test_pickers_frame.grid_columnconfigure(0, weight=1)
        self._test_pickers: dict[str, TestPicker] = {}
        self._parallel_hint = ctk.CTkLabel(
            self._specific_test_frame,
            text="Clique nos resultados para marcar até dois testes; clique novamente para desmarcar sem fechar a busca.",
            text_color=COLORS["muted"],
            anchor="w",
            justify="left",
        )
        self._parallel_hint.grid(
            row=1, column=0, sticky="ew", padx=(14, 8), pady=(0, 8)
        )
        self._parallel_tests_frame = ctk.CTkFrame(
            self._specific_test_frame, fg_color="transparent"
        )
        self._parallel_tests_frame.grid(
            row=2, column=0, sticky="new", padx=(14, 8), pady=(0, 8)
        )
        self._parallel_remove_buttons: list[ctk.CTkButton] = []
        self._parallel_path_labels: list[ctk.CTkLabel] = []
        self._wraplength_after_id: str | None = None
        self._parallel_tests_label = ctk.CTkLabel(
            self._parallel_tests_frame,
            text="Execução paralela: selecione até dois arquivos.",
            text_color=COLORS["muted"],
            anchor="w",
            justify="left",
        )
        self._parallel_tests_label.pack(anchor="nw", fill="x")
        self._all_clients_check = ctk.CTkCheckBox(
            self._specific_test_frame,
            text="Executar em todos os clientes compatíveis",
            fg_color=COLORS["accent_fill"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["ink"],
            command=self._all_clients_changed,
        )
        self._all_clients_check.grid(
            row=1, column=1, sticky="nw", padx=(8, 14), pady=(2, 8)
        )
        self._eligible_clients_label = ctk.CTkLabel(
            self._specific_test_frame,
            text="Clientes compatíveis: selecione um teste.",
            text_color=COLORS["muted"],
            anchor="w",
            justify="left",
        )
        self._eligible_clients_label.grid(
            row=2, column=1, sticky="new", padx=(8, 14), pady=(0, 8)
        )
        count_controls = ctk.CTkFrame(self._specific_test_frame, fg_color="transparent")
        count_controls.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 8)
        )
        ctk.CTkLabel(
            count_controls,
            text="Repetir teste",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(0, 10))
        self._count_picker = ClientPicker(
            count_controls,
            clients={value: value for value in ("1", "2", "3")},
            active_client_key="1",
            on_selected=self._count_changed,
            width=76,
            searchable=False,
        )
        self._count_picker.grid_propagate(False)
        self._count_picker.pack(side="left")
        self._count_summary = ctk.CTkLabel(
            count_controls,
            text="Até 3 processos Pytest (1 × 3 tentativas)",
            text_color=COLORS["muted"],
            anchor="w",
        )
        self._count_summary.pack(side="left", padx=(12, 0))
        self._test_warning = ctk.CTkLabel(
            self._specific_test_frame,
            text="Teste específico ignora a ordem da jornada e não executa pré-condições.",
            text_color=COLORS["orange"],
            anchor="w",
            justify="left",
        )
        self._test_warning.grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14)
        )
        self._specific_test_frame.bind(
            "<Configure>", self._schedule_specific_test_wraplengths, add="+"
        )
        for widget in (
            self._parallel_hint,
            self._parallel_tests_frame,
            self._eligible_clients_label,
            self._test_warning,
        ):
            widget.bind(
                "<Configure>", self._schedule_specific_test_wraplengths, add="+"
            )
        self._selection_label = ctk.CTkLabel(
            card,
            text="Nenhuma jornada selecionada",
            anchor="w",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=12),
        )
        self._selection_label.grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=24, pady=(4, 8)
        )
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=5, column=0, columnspan=2, sticky="ew", padx=24, pady=(4, 0))
        actions.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="sentinel_actions")
        self._execution_status = ctk.CTkLabel(
            actions,
            text="Aguardando execução",
            anchor="w",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=12),
        )
        self._execution_status.grid(
            row=0, column=0, columnspan=5, sticky="ew", padx=4, pady=(0, 6)
        )
        self._selection_notice_var = StringVar(value="")
        self._selection_notice_label = ctk.CTkLabel(
            card,
            textvariable=self._selection_notice_var,
            text_color=COLORS["orange"],
            anchor="w",
            font=ctk.CTkFont(size=11),
        )
        self._selection_notice_label.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 4)
        )
        self._notice_visible = True
        self._start_button = ctk.CTkButton(
            actions,
            text="Iniciar",
            fg_color=COLORS["sentinel_fill"],
            hover_color=COLORS["sentinel_hover"],
            border_width=1,
            border_color=COLORS["sentinel_text"],
            text_color="#FFFFFF",
            command=self._start_clicked,
        )
        self._start_button.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 2))
        self._stop_button = ctk.CTkButton(
            actions,
            text="Parar",
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["ink"],
            text_color_disabled=COLORS["muted"],
            command=self._on_stop,
            state="disabled",
        )
        self._stop_button.grid(row=1, column=1, sticky="ew", padx=4, pady=(0, 2))
        self._pause_button = ctk.CTkButton(
            actions,
            text="Pausar",
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["ink"],
            text_color_disabled=COLORS["muted"],
            command=self._on_pause,
            state="disabled",
        )
        self._pause_button.grid(row=1, column=2, sticky="ew", padx=4, pady=(0, 2))
        self._open_report_button = ctk.CTkButton(
            actions,
            text="Abrir relatório",
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["ink"],
            text_color_disabled=COLORS["muted"],
            command=self._on_open_report,
            state="disabled",
        )
        self._open_report_button.grid(row=1, column=3, sticky="ew", padx=4, pady=(0, 2))
        self._open_folder_button = ctk.CTkButton(
            actions,
            text="Abrir pasta",
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["ink"],
            text_color_disabled=COLORS["muted"],
            command=self._on_open_folder,
            state="disabled",
        )
        self._open_folder_button.grid(row=1, column=4, sticky="ew", padx=4, pady=(0, 2))
        self._trace_picker = ClientPicker(
            actions,
            clients={"Nenhum trace disponível": "Nenhum trace disponível"},
            active_client_key="Nenhum trace disponível",
            on_selected=self._trace_changed,
            width=250,
            searchable=False,
        )
        self._trace_picker.grid_propagate(False)
        self._trace_picker.grid(row=2, column=0, columnspan=4, sticky="ew", padx=4, pady=(8, 14))
        self._trace_picker.set_enabled(False)
        self._open_trace_button = ctk.CTkButton(
            actions,
            text="Abrir trace",
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["ink"],
            text_color_disabled=COLORS["muted"],
            command=self._open_selected_trace,
            state="disabled",
        )
        self._open_trace_button.grid(row=2, column=4, sticky="ew", padx=4, pady=(8, 14))
        execution_header = ctk.CTkFrame(card, fg_color="transparent")
        execution_header.grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=24, pady=(14, 18)
        )
        execution_header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            execution_header,
            text="Saída da execução",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))
        self._execution_picker = ClientPicker(
            execution_header,
            clients={"Nenhuma execução": "Nenhuma execução"},
            active_client_key="Nenhuma execução",
            on_selected=self._execution_changed,
            width=260,
            searchable=False,
            max_visible_rows=7,
        )
        self._execution_picker.grid_propagate(False)
        self._execution_picker.grid(row=0, column=1, sticky="ew")
        self._execution_picker.set_enabled(False)
        self._execution_state_label = ctk.CTkLabel(
            execution_header,
            text="Sem execução selecionada",
            text_color=COLORS["muted"],
            anchor="e",
        )
        self._execution_state_label.grid(row=1, column=0, columnspan=3, sticky="e")
        self._execution_metrics_label = ctk.CTkLabel(
            execution_header,
            text="Recursos: aguardando amostra",
            text_color=COLORS["muted"],
            anchor="e",
        )
        self._execution_metrics_label.grid(row=2, column=0, columnspan=3, sticky="e")
        execution_panel = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
        )
        execution_panel.grid(
            row=2, column=0, sticky="ew", padx=32, pady=(14, 26)
        )
        execution_panel.grid_columnconfigure(0, weight=1)
        log_header = ctk.CTkFrame(execution_panel, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 4))
        log_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            log_header,
            text="Painel de logs",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        self._expand_logs_button = ctk.CTkButton(
            log_header,
            text="Expandir",
            width=74,
            height=28,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            text_color=COLORS["muted"],
            command=self._on_toggle_logs,
        )
        self._expand_logs_button.grid(row=0, column=1, sticky="e")
        self._copy_logs_button = ctk.CTkButton(
            log_header,
            text="Copiar",
            width=64,
            height=28,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            text_color=COLORS["muted"],
            command=self._copy_execution_log,
        )
        self._copy_logs_button.grid(row=0, column=2, sticky="e", padx=(6, 0))
        self._execution_log = ctk.CTkTextbox(
            execution_panel,
            height=110,
            fg_color=COLORS["surface_alt"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=11),
            state="disabled",
        )
        self._execution_log.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
        self.protect_textbox(self._execution_log)
        self._expanded_modules: set[str] = set()
        self.set_modules(modules)
        self.set_tests(tests)
        self.set_plans(())

    def set_logs_expanded(self, expanded: bool) -> None:
        """Amplia a saída sem ocultar os controles da Sentinela."""
        self._logs_expanded = expanded
        self._execution_log.configure(
            height=max(320, int(self.winfo_toplevel().winfo_height() * 0.6))
            if expanded else 110
        )
        self._expand_logs_button.configure(text="Restaurar" if expanded else "Expandir")

    def _copy_execution_log(self) -> None:
        """Copia o texto atualmente visível no painel da Sentinela."""
        content = self._execution_log.get("1.0", "end-1c")
        if not content:
            return
        self.clipboard_clear()
        self.clipboard_append(content)

    def set_log_font_size(self, size: int) -> None:
        """Altera somente a fonte do painel de execução."""
        self._execution_log.configure(font=ctk.CTkFont(size=size))

    def resize_expanded_logs(self) -> None:
        """Mantém a área ampliada proporcional à janela."""
        if self._logs_expanded and self.winfo_exists():
            self._execution_log.configure(
                height=max(320, int(self.winfo_toplevel().winfo_height() * 0.6))
            )

    def scroll_to_logs(self) -> None:
        """Mostra a área ampliada após a ação do usuário."""
        if self.winfo_exists():
            self.update_idletasks()
            self._parent_canvas.yview_moveto(1.0)

    def _mode_changed(self, label: str) -> None:
        if self._running:
            return
        mode = next(mode for mode in SentinelRunMode if mode.value == label)
        if mode is self._mode:
            return
        self._mode = mode
        self._mode_picker.set_active_client(label)
        self._count = 1
        self._count_picker.set_active_client("1")
        self._update_count_summary()
        self._on_count_selected(1)
        self._run_all_clients = False
        self._all_clients_check.deselect()
        self._on_all_clients_selected(False)
        self.set_eligible_clients(())
        self._selected_test = None
        self._plans = ()
        self._selected_modules.clear()
        self._selection_label.configure(
            text="Nenhum teste selecionado" if mode is SentinelRunMode.SPECIFIC_TEST else "Nenhuma jornada selecionada"
        )
        self._on_mode_selected(mode)
        self._render_mode()

    def _count_changed(self, value: str) -> None:
        if self._running:
            return
        self._count_picker.set_active_client(value)
        self._count = int(value)
        self._on_count_selected(self._count)
        self._update_count_summary()

    def _update_count_summary(self) -> None:
        clients = len(self._eligible_client_labels) if self._run_all_clients else 1
        targets = 1 if self._run_all_clients else max(1, len(self._parallel_tests))
        maximum = self._count * self._retry_limit * clients * targets
        self._count_summary.configure(
            text=(
                f"Até {maximum} processos Pytest "
                f"({clients} clientes × {targets} testes × {self._count} × {self._retry_limit} tentativas)"
            )
        )
        self._refresh_start_button()

    def _refresh_start_button(self) -> None:
        if self._free_slots == 0 or (
            self._running and self._mode is not SentinelRunMode.JOURNEY
        ):
            self._start_button.configure(state="disabled")
            return
        can_start = (
            self._selected_test is not None
            and (
                (self._run_all_clients and bool(self._eligible_client_labels))
                or (
                    not self._run_all_clients
                    and
                    1 <= (len(self._parallel_tests) or 1) <= 2
                    and (len(self._parallel_tests) != 2 or self._count == 1)
                )
            )
            if self._mode is SentinelRunMode.SPECIFIC_TEST
            else 1 <= len(self._plans) <= self._free_slots
            and all(plan.can_start for plan in self._plans)
            and all(plan.module_prefix not in self._active_targets for plan in self._plans)
        )
        if self._mode is SentinelRunMode.JOURNEY and can_start:
            can_start = not self._run_all_clients and self._count == 1
        self._start_button.configure(state="normal" if can_start else "disabled")

    def _all_clients_changed(self) -> None:
        if self._running:
            return
        self._run_all_clients = bool(self._all_clients_check.get())
        self._on_all_clients_selected(self._run_all_clients)
        self._update_count_summary()

    def _start_clicked(self) -> None:
        if self._mode is SentinelRunMode.SPECIFIC_TEST and self._run_all_clients:
            if self._selected_test is None or not self._eligible_client_labels:
                return
            process_limit = (
                len(self._eligible_client_labels) * self._count * self._retry_limit
            )
            details = (
                f"Teste: {self._selected_test.path}\n\n"
                f"Clientes elegíveis ({len(self._eligible_client_labels)}):\n"
                f"{chr(10).join(self._eligible_client_labels)}\n\n"
                f"Repetições: {self._count}\n"
                f"Limite máximo: {process_limit} processos Pytest "
                f"({len(self._eligible_client_labels)} × {self._count} × {self._retry_limit}).\n\n"
                "Deseja iniciar a execução sequencial em todos os clientes?"
            )
            if not messagebox.askyesno("Confirmar execução multi-cliente", details, parent=self):
                return
        self._on_start()

    def set_eligible_clients(self, labels: Sequence[str]) -> None:
        """Atualiza a lista e o custo previstos para a seleção atual."""
        self._eligible_client_labels = tuple(
            sorted(labels, key=_client_label_sort_key)
        )
        if self._eligible_client_labels:
            self._eligible_clients_label.configure(
                text=(
                    f"Clientes compatíveis ({len(self._eligible_client_labels)}): "
                    + ", ".join(self._eligible_client_labels)
                )
            )
        else:
            self._eligible_clients_label.configure(text="Clientes compatíveis: nenhum.")
        self._update_count_summary()

    def _schedule_specific_test_wraplengths(self, _event: object = None) -> None:
        """Recalcula a quebra dos textos conforme as colunas disponíveis."""
        if (
            not self._specific_test_frame.winfo_exists()
            or self._wraplength_after_id is not None
        ):
            return
        self._wraplength_after_id = self.after_idle(
            self._update_specific_test_wraplengths
        )

    def _update_specific_test_wraplengths(self) -> None:
        """Mantém textos longos dentro da coluna sem invadir os botões."""
        self._wraplength_after_id = None
        if not self._specific_test_frame.winfo_exists():
            return
        for label in (self._parallel_hint, self._parallel_tests_label):
            width = label.winfo_width() - 24
            if width > 80 and label.cget("wraplength") != width:
                label.configure(wraplength=width)
        for label in self._parallel_path_labels:
            width = label.winfo_width() - 12
            if width > 80 and label.cget("wraplength") != width:
                label.configure(wraplength=width)
        width = self._eligible_clients_label.winfo_width() - 24
        if width > 80 and self._eligible_clients_label.cget("wraplength") != width:
            self._eligible_clients_label.configure(wraplength=width)
        width = self._test_warning.winfo_width() - 28
        if width > 80 and self._test_warning.cget("wraplength") != width:
            self._test_warning.configure(wraplength=width)

    def set_run_all_clients(self, enabled: bool) -> None:
        """Sincroniza a opção multi-cliente depois de trocar cliente ou modo."""
        self._run_all_clients = enabled
        self._all_clients_check.deselect() if not enabled else self._all_clients_check.select()
        self._update_count_summary()
        if self._mode is SentinelRunMode.JOURNEY:
            self.set_plans(self._plans)

    def _render_mode(self) -> None:
        if self._mode is SentinelRunMode.SPECIFIC_TEST:
            self._count_picker.set_enabled(not self._running)
            self._module_title.grid_remove()
            self._plan_title.grid_configure(
                row=1, column=0, columnspan=2, sticky="ew", padx=24, pady=(8, 10)
            )
            self._module_list.grid_remove()
            self._plan_content.grid_remove()
            self._selection_notice_label.grid_remove()
            self._notice_visible = False
            self._specific_test_frame.grid(
                row=2, column=0, columnspan=2, sticky="nsew", padx=24, pady=(0, 12)
            )
            self._plan_title.configure(text="Teste específico · prévia")
            self.set_selected_test(self._selected_test)
        else:
            self._count_picker.set_enabled(False)
            self._module_title.grid()
            self._plan_title.grid_configure(
                row=1, column=1, columnspan=1, sticky="ew", padx=(12, 24), pady=(8, 10)
            )
            self._specific_test_frame.grid_remove()
            self._selection_notice_label.grid(
                row=3, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 4)
            )
            self._module_list.grid(row=2, column=0, sticky="nsew", padx=(24, 12), pady=(0, 12))
            self._plan_content.grid(row=2, column=1, sticky="nsew", padx=(12, 24), pady=(0, 12))
            self._plan_title.configure(
                text=f"Prévia do lote · {len(self._plans)}/2 jornadas"
            )
            self._set_plan_text(
                "Selecione uma jornada para iniciar ou adicione outra para execução paralela."
            )
            self._refresh_start_button()

    def set_mode(self, mode: SentinelRunMode) -> None:
        """Sincroniza o modo coordenado pelo controlador."""
        self._mode = mode
        self._selected_test = None
        for picker in self._test_pickers.values():
            picker.set_selected_item(None)
        self.set_plans(())
        self._count = 1
        self._count_picker.set_active_client("1")
        self._update_count_summary()
        self._run_all_clients = False
        self.set_parallel_tests(())
        self._all_clients_check.deselect()
        self.set_eligible_clients(())
        self._mode_picker.set_active_client(mode.value)
        self._render_mode()

    def set_count(self, count: int) -> None:
        """Sincroniza a repetição local com o controlador."""
        self._count = count
        self._count_picker.set_active_client(str(count))
        self._update_count_summary()

    def set_tests(self, tests: Sequence[TestItem]) -> None:
        """Atualiza os arquivos filtrados do catálogo para o cliente atual."""
        self._tests = tuple(tests)
        self._selected_test = None
        self._parallel_tests = ()
        self.set_parallel_tests(())
        self._render_test_pickers()
        self.set_eligible_clients(())
        if self._mode is SentinelRunMode.SPECIFIC_TEST:
            self.set_selected_test(None)

    def _render_test_pickers(self) -> None:
        """Agrupa os testes elegíveis nos seletores dos módulos do catálogo."""
        grouped: dict[str, list[TestItem]] = {}
        for item in self._tests:
            grouped.setdefault(item.module, []).append(item)
        old_columns = self._test_pickers_frame.grid_size()[0]
        for picker in self._test_pickers.values():
            picker.destroy()
        self._test_pickers.clear()
        for column in range(old_columns):
            self._test_pickers_frame.grid_columnconfigure(column, weight=0, uniform="")
        for column, (module, items) in enumerate(grouped.items()):
            self._test_pickers_frame.grid_columnconfigure(column, weight=1, uniform="test_modules")
            picker = TestPicker(
                self._test_pickers_frame,
                items=items,
                on_selected=self._test_changed,
                width=150,
                placeholder="Específicos" if module == "Testes Específicos" else module,
                show_selected_item=False,
                on_multi_toggle=self._on_test_toggled,
            )
            picker.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 4, 4))
            picker.set_enabled(not self._running)
            self._test_pickers[module] = picker

    def _test_changed(self, selection_id: str) -> None:
        if self._running:
            return
        item = next(
            (candidate for candidate in self._tests if candidate.selection_id == selection_id),
            None,
        )
        self._selected_test = item
        self._on_test_selected(item.selection_id if item is not None else "")
        self.set_selected_test(item)

    def set_selected_test(self, item: TestItem | None) -> None:
        """Apresenta o alvo selecionado e controla a disponibilidade de início."""
        self._selected_test = item
        for picker in self._test_pickers.values():
            picker.set_selected_item(item)
        self._refresh_specific_test_preview()

    def set_picker_multi_selection(self, selection_ids: Sequence[str]) -> None:
        """Apresenta nos resultados os testes confirmados no lote paralelo."""
        for picker in self._test_pickers.values():
            picker.set_multi_selected_items(selection_ids)

    def _refresh_specific_test_preview(self) -> None:
        """Mostra os arquivos que a Sentinela receberá na seleção atual."""
        if self._mode is not SentinelRunMode.SPECIFIC_TEST:
            return
        if self._parallel_tests and not self._run_all_clients:
            total = len(self._parallel_tests)
            self._plan_title.configure(text=f"Testes específicos · {total} arquivo{'s' if total != 1 else ''}")
            self._selection_label.configure(text=f"Lote selecionado: {total}/2 testes")
            self._set_plan_text(
                "Alvos enviados à Sentinela:\n"
                + "\n".join(item.path for item in self._parallel_tests)
                + "\n\nPré-condições da jornada não serão executadas."
            )
        elif self._selected_test is None:
            self._plan_title.configure(text="Teste específico · prévia")
            self._selection_label.configure(text="Nenhum teste selecionado")
            self._set_plan_text("Selecione um teste disponível para visualizar o alvo.")
        else:
            self._plan_title.configure(text="Teste específico · 1 arquivo")
            self._selection_label.configure(text=f"Teste selecionado: {self._selected_test.path}")
            self._set_plan_text(
                f"Alvo enviado à Sentinela:\n{self._selected_test.path}\n\n"
                "Pré-condições da jornada não serão executadas."
            )
        self._refresh_start_button()

    def set_parallel_tests(self, items: Sequence[TestItem]) -> None:
        """Apresenta a seleção explícita de até dois arquivos específicos."""
        self._parallel_tests = tuple(items)
        selected_ids = tuple(item.selection_id for item in items)
        self.set_picker_multi_selection(selected_ids)
        for child in self._parallel_tests_frame.winfo_children():
            if child is not self._parallel_tests_label:
                child.destroy()
        self._parallel_remove_buttons.clear()
        self._parallel_path_labels.clear()
        self._parallel_tests_label.configure(
            text=(
                f"Execução paralela ({len(items)}/2):"
                if items else "Execução paralela: selecione até dois arquivos."
            )
        )
        for item in items:
            row = ctk.CTkFrame(self._parallel_tests_frame, fg_color="transparent")
            row.pack(fill="x", pady=(4, 0))
            path_label = ctk.CTkLabel(
                row,
                text=item.path,
                anchor="w",
                justify="left",
                text_color=COLORS["ink"],
            )
            path_label.pack(
                side="left", fill="x", expand=True
            )
            self._parallel_path_labels.append(path_label)
            path_label.bind(
                "<Configure>", self._schedule_specific_test_wraplengths, add="+"
            )
            button = ctk.CTkButton(
                row,
                text="Remover",
                width=80,
                fg_color=COLORS["sentinel_fill"],
                hover_color=COLORS["sentinel_hover"],
                command=lambda selection_id=item.selection_id: self._on_test_removed(selection_id),
                state="disabled" if self._running else "normal",
            )
            button.pack(side="right", padx=(8, 0))
            self._parallel_remove_buttons.append(button)
        self._refresh_specific_test_preview()
        self._update_count_summary()
        self._schedule_specific_test_wraplengths()

    def _set_plan_text(self, text: str) -> None:
        self._plan_content.configure(state="normal")
        self._plan_content.delete("1.0", "end")
        self._plan_content.insert("1.0", text)
        self._plan_content.configure(state="disabled")

    def set_client_modules(
        self, client_key: str, modules: Sequence[SentinelModule]
    ) -> None:
        """Troca o cliente, limpa a escolha e apresenta as jornadas atualizadas."""
        self._client_picker.set_active_client(client_key)
        self._selected_modules.clear()
        self._selection_label.configure(text="Nenhuma jornada selecionada")
        self._selection_notice_var.set("")
        self.set_plans(())
        self._expanded_modules = set()
        self.set_modules(modules)
        self.set_selected_test(None)

    def restore_selections(self, plans: Sequence[SentinelPlan]) -> None:
        """Restaura as jornadas escolhidas quando a página é recriada."""
        self.set_plans(plans)

    def set_artifacts(self, artifacts: SentinelRunArtifacts) -> None:
        """Habilita ações somente para os artefatos validados pelo serviço."""
        if artifacts == self._artifacts:
            return
        self._artifacts = artifacts
        self._open_report_button.configure(
            state="normal" if artifacts.report_path is not None else "disabled"
        )
        self._open_folder_button.configure(
            state="normal" if artifacts.folder_path is not None else "disabled"
        )
        paths = tuple(artifacts.trace_paths)
        labels = [path.name for path in paths]
        if len(set(labels)) != len(labels):
            labels = [f"{index}. {path.name}" for index, path in enumerate(paths, 1)]
        self._trace_paths = dict(zip(labels, paths))
        trace_options = (
            {"Selecione um trace": "Selecione um trace", **{label: label for label in labels}}
            if labels
            else {"Nenhum trace disponível": "Nenhum trace disponível"}
        )
        trace_default = "Selecione um trace" if labels else "Nenhum trace disponível"
        self._trace_picker.set_options(trace_options, trace_default)
        self._trace_picker.set_enabled(bool(labels))
        self._open_trace_button.configure(state="disabled")

    def set_execution_records(
        self,
        executions: Sequence[
            tuple[str, str, str, Sequence[str], str]
            | tuple[str, str, str, Sequence[str], str, bool]
        ],
        selected_execution_id: str | None,
        can_control_selected: bool = False,
    ) -> None:
        """Atualiza o seletor e mostra somente a saída da execução selecionada."""
        labels: list[str] = []
        selected = None
        selected_state = None
        selected_output: Sequence[str] = ()
        selected_metrics = "Recursos: aguardando amostra"
        self._execution_ids_by_label.clear()
        historical_by_id: dict[str, bool] = {}
        for entry in executions:
            execution_id, target, state, output, metrics = entry[:5]
            historical = bool(entry[5]) if len(entry) > 5 else False
            label = f"{target} · {state} · {execution_id}"
            self._execution_ids_by_label[label] = execution_id
            historical_by_id[execution_id] = historical
            labels.append(label)
            if execution_id == selected_execution_id:
                selected = label
                selected_state = state
                selected_output = output
                selected_metrics = metrics
        if not labels:
            self._pause_button.configure(text="Pausar", state="disabled")
            self._stop_button.configure(state="disabled")
            self._execution_metrics_label.configure(text="Recursos: indisponível")
            if self._execution_labels_cache:
                self._execution_picker.set_options(
                    {"Nenhuma execução": "Nenhuma execução"}, "Nenhuma execução"
                )
                self._execution_picker.set_enabled(False)
                self._execution_labels_cache = ()
            if self._execution_selection_cache is not None:
                self._execution_picker.set_active_client("Nenhuma execução")
                self._execution_selection_cache = None
            if self._execution_state_cache != "":
                self._execution_state_label.configure(
                    text="Sem execução selecionada", text_color=COLORS["muted"]
                )
                self._execution_state_cache = ""
            self.set_execution_log(())
            return
        label_values = tuple(labels)
        if label_values != self._execution_labels_cache:
            self._execution_picker.set_options(
                {label: label for label in labels},
                selected or labels[-1],
            )
            self._execution_picker.set_enabled(True)
            self._execution_labels_cache = label_values
        if selected is None:
            selected = labels[-1]
            selected_execution_id = self._execution_ids_by_label[selected]
            selected_entry = next(
                item for item in executions if item[0] == selected_execution_id
            )
            selected_state = selected_entry[2]
            selected_output = selected_entry[3]
            selected_metrics = selected_entry[4]
        is_historical = historical_by_id.get(selected_execution_id or "", False)
        if self._execution_selection_cache != selected:
            self._execution_picker.set_active_client(selected)
            self._execution_selection_cache = selected
        if self._execution_state_cache != selected_state:
            is_success = selected_state in {
                "SUCCEEDED",
                "Histórico · SEM FALHAS DETECTADAS",
            }
            is_failure = selected_state in {
                "FAILED",
                "Histórico · COM FALHAS",
                "INTERRUPTED",
                "PAUSE_REQUESTED",
                "PAUSED_BETWEEN_TESTS",
            } or (selected_state or "").startswith(
                ("Histórico · FAILED", "Histórico · INTERRUPTED")
            )
            self._execution_state_label.configure(
                text=f"Estado: {selected_state}",
                text_color=(
                    COLORS["success"]
                    if is_success
                    else COLORS["orange"]
                    if is_failure
                    else COLORS["muted"]
                ),
            )
            self._execution_state_cache = selected_state
        pause_text = (
            "Continuar" if selected_state == "PAUSED_BETWEEN_TESTS"
            else "Cancelar pausa" if selected_state == "PAUSE_REQUESTED"
            else "Pausar"
        )
        pause_state = (
            "normal"
            if not is_historical and selected_state == "PAUSE_REQUESTED"
            or (can_control_selected and selected_state in {"RUNNING", "PAUSED_BETWEEN_TESTS"})
            else "disabled"
        )
        stoppable = any(
            entry[2] in {"STARTING", "RUNNING", "PAUSE_REQUESTED", "PAUSED_BETWEEN_TESTS"}
            for entry in executions
        )
        self._stop_button.configure(state="normal" if stoppable else "disabled")
        if (
            self._pause_button.cget("text") != pause_text
            or self._pause_button.cget("state") != pause_state
        ):
            self._pause_button.configure(text=pause_text, state=pause_state)
        self.set_execution_log(selected_output, selected_execution_id)
        if self._execution_metrics_label.cget("text") != selected_metrics:
            self._execution_metrics_label.configure(text=selected_metrics)

    def set_execution_log(
        self, lines: Sequence[str], source: str | None = None
    ) -> None:
        """Mostra a saída de uma execução, acrescentando só as linhas novas.

        ``lines`` só cresce para a mesma ``source`` (a saída do registro é
        append-only); trocar de execução redesenha a caixa.
        """
        count = len(lines)
        key = self._execution_log_key
        if key == (source, count):
            return
        append_only = (
            key is not None
            and key[0] == source
            and key[1] < count <= key[1] + self.MAX_LOG_LINES
        )
        follow_tail = self._execution_log.yview()[1] >= 0.999
        self._execution_log_key = (source, count)
        self._execution_log.configure(state="normal")
        if not append_only:
            self._execution_log.delete("1.0", END)
        added = (
            lines[key[1]:]
            if append_only and key is not None
            else lines[max(0, count - self.MAX_LOG_LINES):]
        )
        if added:
            self._execution_log.insert(END, "\n".join(added) + "\n")
            line_count = int(self._execution_log.index("end-1c").split(".")[0])
            if line_count > self.MAX_LOG_LINES:
                self._execution_log.delete(
                    "1.0", f"{line_count - self.MAX_LOG_LINES + 1}.0"
                )
        if not append_only or follow_tail:
            self._execution_log.see(END)
        self._execution_log.configure(state="disabled")

    def _execution_changed(self, label: str) -> None:
        execution_id = self._execution_ids_by_label.get(label)
        if execution_id is not None:
            self._on_execution_selected(execution_id)

    def _trace_changed(self, label: str) -> None:
        self._trace_picker.set_active_client(label)
        self._open_trace_button.configure(
            state="normal" if label in self._trace_paths else "disabled"
        )

    def _open_selected_trace(self) -> None:
        label = self._trace_picker.active_client_key
        path = self._trace_paths.get(label)
        if path is not None:
            self._on_open_trace(path)

    def set_modules(self, modules: Sequence[SentinelModule]) -> None:
        """Atualiza a lista na ordem recebida pelo serviço de plano.

        Só recria os botões quando a árvore ou a expansão mudam; seleção e
        bloqueio durante a execução apenas reconfiguram os botões existentes.
        """
        self._modules = tuple(modules)
        render_key = (self._modules, frozenset(self._expanded_modules))
        if render_key != self._module_render_key:
            self._module_render_key = render_key
            self._rebuild_module_buttons()
        self._refresh_module_buttons()

    def _rebuild_module_buttons(self) -> None:
        """Recria a árvore visível de jornadas no estado neutro."""
        for child in self._module_list.winfo_children():
            child.destroy()
        self._module_buttons.clear()

        selectable = [module for module in self._modules if module.path != "tests"]
        if not selectable:
            ctk.CTkLabel(
                self._module_list,
                text="Nenhuma jornada disponível para este cliente.",
                text_color=COLORS["muted"],
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return

        modules_by_path = {module.path: module for module in selectable}
        children: dict[str, list[SentinelModule]] = {}
        roots: list[SentinelModule] = []
        for module in selectable:
            if module.parent_path in (None, "tests"):
                roots.append(module)
            elif module.parent_path in modules_by_path:
                children.setdefault(module.parent_path, []).append(module)

        visible: list[tuple[SentinelModule, int]] = []

        def append_visible(module: SentinelModule, depth: int) -> None:
            visible.append((module, depth))
            if module.path in self._expanded_modules:
                for child in children.get(module.path, ()):
                    append_visible(child, depth + 1)

        for root in roots:
            append_visible(root, 0)

        for row, (module, depth) in enumerate(visible):
            descendants = children.get(module.path, [])
            row_frame = ctk.CTkFrame(self._module_list, fg_color="transparent")
            row_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
            row_frame.grid_columnconfigure(1, weight=1)
            expand_button: ctk.CTkButton | None = None
            if descendants:
                expanded = module.path in self._expanded_modules
                expand_button = ctk.CTkButton(
                    row_frame,
                    text="⌄" if expanded else "›",
                    width=30,
                    height=36,
                    fg_color="transparent",
                    hover_color=COLORS["surface"],
                    text_color=COLORS["ink"],
                    command=lambda path=module.path: self._toggle_expansion(path),
                )
                expand_button.grid(row=0, column=0, padx=(depth * 24, 4))
            else:
                ctk.CTkLabel(row_frame, text="", width=30).grid(
                    row=0, column=0, padx=(depth * 24, 4)
                )

            title = module.path.split("/")[-1].replace("_", " ").capitalize()
            if module.explicit_only:
                title += " · explícito"
            module_button = ctk.CTkButton(
                row_frame,
                text=title,
                anchor="w",
                height=36,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLORS["surface"],
                border_width=1,
                border_color=COLORS["border"],
                text_color=COLORS["ink"],
                command=lambda path=module.path: self._select_module(path),
            )
            module_button.grid(row=0, column=1, sticky="ew")
            module_button.bind(
                "<FocusIn>",
                lambda _event=None, button=module_button, path=module.path: self._style_module_focus(
                    button, True, path in self._selected_modules
                ),
            )
            module_button.bind(
                "<FocusOut>",
                lambda _event=None, button=module_button, path=module.path: self._style_module_focus(
                    button, False, path in self._selected_modules
                ),
            )
            self._module_buttons[module.path] = _ModuleButtons(
                module_button, expand_button, title
            )

    def _refresh_module_buttons(self) -> None:
        """Aplica seleção e bloqueio só aos botões cujo estado mudou."""
        for path, widgets in self._module_buttons.items():
            state = (
                "disabled"
                if self._free_slots == 0 or path in self._active_targets
                else "normal"
            )
            applied = (path in self._selected_modules, state)
            if applied == widgets.applied:
                continue
            selected = applied[0]
            widgets.module_button.configure(
                text=f"✓  {widgets.title}" if selected else widgets.title,
                fg_color=COLORS["sentinel_fill"] if selected else "transparent",
                hover_color=COLORS["sentinel_hover"] if selected else COLORS["surface"],
                border_width=2 if selected else 1,
                border_color=COLORS["surface"] if selected else COLORS["border"],
                text_color="#FFFFFF" if selected else COLORS["ink"],
                state=state,
            )
            widgets.applied = applied

    def set_capacity(self, free_slots: int, active_targets: set[str]) -> None:
        """Atualiza somente a capacidade e o bloqueio das jornadas ativas."""
        if free_slots == self._free_slots and active_targets == self._active_targets:
            return
        self._free_slots = free_slots
        self._active_targets = set(active_targets)
        self._module_title.configure(
            text=(
                "Jornadas disponíveis · até duas"
                if free_slots == 2
                else "Jornadas disponíveis · 1 vaga livre"
                if free_slots == 1
                else "Jornadas disponíveis · nenhuma vaga livre"
            )
        )
        self._refresh_module_buttons()
        self._refresh_start_button()

    def choose_stop_targets(
        self, active_runs: Sequence[tuple[str, str]]
    ) -> str | None:
        """Mostra as execuções ativas e devolve o ID escolhido ou 'all'."""
        if not active_runs:
            return None
        dialog = ctk.CTkToplevel(self)
        dialog.title("Parar execução da Sentinela")
        parent = self.winfo_toplevel()
        dialog.transient(parent)
        dialog.resizable(False, False)
        dialog.grid_columnconfigure(0, weight=1)
        choice: list[str | None] = [None]

        def finish(value: str | None) -> None:
            choice[0] = value
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", lambda: finish(None))
        dialog.bind("<Escape>", lambda _event: finish(None))
        ctk.CTkLabel(
            dialog,
            text="Qual execução deseja parar?",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        for row, (execution_id, target) in enumerate(active_runs, 1):
            option = ctk.CTkFrame(dialog, fg_color="transparent")
            option.grid(row=row, column=0, sticky="ew", padx=20, pady=4)
            ctk.CTkLabel(
                option, text=target, anchor="w", wraplength=500,
            ).pack(fill="x")
            ctk.CTkButton(
                option,
                text=f"Parar esta execução · {execution_id[:8]}",
                command=lambda selected_id=execution_id: finish(selected_id),
                anchor="w",
            ).pack(fill="x", pady=(4, 0))
        next_row = len(active_runs) + 1
        if len(active_runs) == 2:
            ctk.CTkButton(
                dialog, text="Parar as duas", command=lambda: finish("all")
            ).grid(row=next_row, column=0, sticky="ew", padx=20, pady=4)
            next_row += 1
        ctk.CTkButton(
            dialog, text="Cancelar", command=lambda: finish(None)
        ).grid(row=next_row, column=0, sticky="ew", padx=20, pady=(4, 20))
        dialog.update_idletasks()
        width = 560
        height = dialog.winfo_reqheight()
        dialog.geometry(
            f"{width}x{height}+{parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)}"
            f"+{parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)}"
        )
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.wait_window()
        return choice[0]

    @staticmethod
    def _style_module_focus(button: ctk.CTkButton, focused: bool, selected: bool) -> None:
        """Ignora eventos tardios quando a lista de jornadas foi recriada."""
        if button.winfo_exists():
            button.configure(
                border_width=2 if focused or selected else 1,
                border_color=(
                    COLORS["ink"] if focused else
                    COLORS["surface"] if selected else COLORS["border"]
                ),
            )

    def _toggle_expansion(self, path: str) -> None:
        if path in self._expanded_modules:
            self._expanded_modules.remove(path)
        else:
            self._expanded_modules.add(path)
        self.set_modules(self._modules)

    def _select_module(self, path: str) -> None:
        self._on_module_selected(path)

    def show_selection_notice(self, message: str) -> None:
        """Explica uma seleção recusada sem modificar as jornadas escolhidas."""
        self._selection_notice_var.set(message)
        self._selection_notice_label.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 4)
        )

    def set_plans(self, plans: Sequence[SentinelPlan]) -> None:
        """Exibe os planos selecionados e a prontidão para iniciar."""
        self._plans = tuple(plans)
        self._selected_modules = {plan.module_prefix for plan in self._plans}
        self._refresh_module_buttons()
        self._selection_notice_var.set("")
        if self._mode is SentinelRunMode.SPECIFIC_TEST:
            return
        self._refresh_start_button()
        if not self._plans:
            self._plan_title.configure(text="Prévia do lote · 0/2 jornadas")
            lines = ["Selecione uma jornada para iniciar ou adicione outra para execução paralela."]
            status = "Nenhuma jornada selecionada."
            status_color = COLORS["muted"]
            selection = "Jornadas selecionadas: 0/2"
        else:
            total_occurrences = sum(plan.occurrence_count for plan in self._plans)
            self._plan_title.configure(
                text=(
                    f"{'Prévia da jornada' if len(self._plans) == 1 else 'Prévia do lote'} · "
                    f"{len(self._plans)}/2 jornadas · "
                    f"{total_occurrences} ocorrências"
                )
            )
            selection = (
                "Jornadas selecionadas: "
                + " + ".join(plan.module_prefix for plan in self._plans)
                + (" · 1/2" if len(self._plans) == 1 else " · 2/2")
            )
            lines = []
            invalid_lines: list[str] = []
            for position, plan in enumerate(self._plans, 1):
                lines.extend(
                    (
                        f"Jornada {position}: {plan.module_prefix} · "
                        f"{plan.occurrence_count} ocorrências",
                        *(
                            f"  {occurrence.index}. {occurrence.path}"
                            for occurrence in plan.occurrences
                        ),
                        "",
                    )
                )
                invalid_lines.extend(plan.invalid_paths)
            if invalid_lines:
                status = "Início bloqueado: há paths inválidos nos planos."
                status_color = COLORS["orange"]
                lines.extend(("Paths inválidos:", *dict.fromkeys(invalid_lines)))
            elif any(not plan.can_start for plan in self._plans):
                status = "Início bloqueado: pelo menos um plano está vazio."
                status_color = COLORS["orange"]
            elif len(self._plans) == 1:
                status = "Uma jornada pronta para execução."
                status_color = COLORS["success"]
            else:
                status = "Duas jornadas prontas para execução em paralelo."
                status_color = COLORS["success"]

        if self._mode is SentinelRunMode.JOURNEY and self._run_all_clients:
            status = "Modo multi-cliente disponível somente para teste específico."
            status_color = COLORS["orange"]

        self._plan_content.configure(state="normal")
        self._plan_content.delete("1.0", "end")
        self._plan_content.insert("1.0", "\n".join(lines))
        self._plan_content.tag_config("warning", foreground=COLORS["orange"])
        self._plan_content.configure(state="disabled")
        self._plan_content.see("1.0")
        self._selection_label.configure(text=selection, text_color=COLORS["muted"])
        self._execution_status.configure(text=status, text_color=status_color)
        self._refresh_start_button()

    def set_running(self, running: bool, status: str | None = None) -> None:
        """Bloqueia cliente e modo enquanto há execuções ativas."""
        if running != self._running:
            self._running = running
            self._client_picker.set_enabled(not running)
            for picker in self._test_pickers.values():
                picker.set_enabled(not running)
            for button in self._parallel_remove_buttons:
                button.configure(state="disabled" if running else "normal")
            self._mode_picker.set_enabled(not running)
            self._all_clients_check.configure(state="disabled" if running else "normal")
            self._count_picker.set_enabled(
                not running and self._mode is SentinelRunMode.SPECIFIC_TEST
            )
            self._refresh_start_button()
            self._refresh_module_buttons()
        if status:
            lowered = status.casefold()
            color = (
                COLORS["orange"]
                if "falh" in lowered or "interromp" in lowered
                else COLORS["success"]
                if "conclu" in lowered
                else COLORS["muted"]
            )
            if (
                self._execution_status.cget("text") != status
                or self._execution_status.cget("text_color") != color
            ):
                self._execution_status.configure(text=status, text_color=color)

    def append_execution_log(self, message: str) -> None:
        """Acrescenta saída da Sentinela sem habilitar edição manual."""
        self._execution_log_key = None
        self._execution_log.configure(state="normal")
        self._execution_log.insert(END, message + "\n")
        self._execution_log.see(END)
        self._execution_log.configure(state="disabled")
