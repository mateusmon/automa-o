"""Página de execução demonstrativa."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

import customtkinter as ctk

from gui_v2.components.client_selector import ClientSelector
from gui_v2.components.log_panel import LogPanel
from gui_v2.components.module_selector import ModuleSelector
from gui_v2.components.page_header import PageHeader
from gui_v2.components.selection_summary import SelectionSummary
from gui_v2.components.smart_scrollable_frame import SmartScrollableFrame
from gui_v2.components.test_catalog import TestCatalog
from gui_v2.models.test_item import TestItem
from gui_v2.theme import COLORS


class ExecutionPage(SmartScrollableFrame):
    """Compõe os componentes visuais da execução sem conhecer engines."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        current_module: str,
        primary_modules: Sequence[str],
        module_colors: Mapping[str, str],
        available_modules: Callable[[], list[str]],
        image_loader: Callable[[str], ctk.CTkImage | None],
        clients: Mapping[str, str],
        active_client_key: str,
        url: str,
        speed_ms: int,
        on_open_codegen: Callable[[], None],
        on_client_selected: Callable[[str], None],
        on_speed_changed: Callable[[int], None],
        on_module_selected: Callable[[str], None],
        on_test_toggled: Callable[[str, bool], None],
        on_section_toggled: Callable[[tuple[str, ...]], None],
        on_clear_selection: Callable[[], None],
        on_run: Callable[[], None],
        on_stop: Callable[[], None],
        on_toggle_logs: Callable[[], None],
        on_toggle_log_mode: Callable[[], None],
        on_clear_logs: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color=COLORS["page"], corner_radius=0)
        self._parent_canvas.configure(yscrollincrement=5)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        PageHeader(
            self,
            "Execução de testes",
            "Selecione o cliente, o módulo e os testes que deseja executar",
        ).grid(row=0, column=0, sticky="ew", padx=32, pady=(26, 16))
        self.client_selector = ClientSelector(
            self,
            clients=clients,
            active_client_key=active_client_key,
            url=url,
            speed_ms=speed_ms,
            on_open_codegen=on_open_codegen,
            on_client_selected=on_client_selected,
            on_speed_changed=on_speed_changed,
        )
        self.client_selector.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 14))

        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=2, column=0, sticky="nsew", padx=32)
        self.workspace.grid_columnconfigure(0, weight=7, uniform="execution_columns")
        self.workspace.grid_columnconfigure(1, weight=3, uniform="execution_columns")
        self.workspace.grid_rowconfigure(1, weight=1)

        self.module_selector = ModuleSelector(
            self.workspace,
            picker_parent=self,
            primary_modules=primary_modules,
            module_colors=module_colors,
            current_module=current_module,
            available_modules=available_modules,
            image_loader=image_loader,
            on_module_selected=on_module_selected,
        )
        self.module_selector.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.module_selector.set_modules(module_colors, current_module)
        self.test_catalog = TestCatalog(
            self.workspace, on_test_toggled=on_test_toggled, on_section_toggled=on_section_toggled
        )
        self.test_catalog.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.selection_summary = SelectionSummary(
            self.workspace, on_run=on_run, on_stop=on_stop,
            on_clear_selection=on_clear_selection,
        )
        self.selection_summary.grid(row=1, column=1, sticky="nsew")
        self.log_panel = LogPanel(
            self,
            on_toggle_expanded=on_toggle_logs,
            on_toggle_complete=on_toggle_log_mode,
            on_clear=on_clear_logs,
        )
        self.log_panel.grid(row=3, column=0, sticky="ew", padx=32, pady=(14, 26))
        self.protect_textbox(self.log_panel._text_box)

    @property
    def url(self) -> str:
        """Devolve a URL exibida no seletor da página."""
        return self.client_selector.url

    def set_client_configuration(self, client_key: str, url: str) -> None:
        """Atualiza os valores de configuração exibidos, sem persistir mudanças."""
        self.client_selector.set_client(client_key, url)

    def set_available_modules(self, colors: Mapping[str, str], current_module: str) -> None:
        """Sincroniza o seletor com o catálogo carregado para o cliente."""
        self.module_selector.set_modules(colors, current_module)
        self.test_catalog.reset_for_client()

    def show_module(
        self,
        module: str,
        module_color: str,
        sections: Mapping[str, Sequence[TestItem]],
        selected_tests: set[str],
        history_by_path: Mapping[str, str],
    ) -> None:
        """Atualiza catálogo, busca e seletor para o módulo ativo."""
        self.test_catalog.clear_search()
        self.test_catalog.render(module, module_color, sections, selected_tests, history_by_path)
        self.module_selector.set_active(module)

    def render_catalog(
        self,
        module: str,
        module_color: str,
        sections: Mapping[str, Sequence[TestItem]],
        selected_tests: set[str],
        history_by_path: Mapping[str, str],
    ) -> None:
        """Atualiza somente o conteúdo do catálogo."""
        self.test_catalog.render(module, module_color, sections, selected_tests, history_by_path)

    def update_catalog_history(self, history_by_path: Mapping[str, str]) -> None:
        """Atualiza indicadores do histórico sem remontar ou rolar o catálogo."""
        self.test_catalog.update_history(history_by_path)

    def render_selection(self, items: Sequence[tuple[str, str]]) -> None:
        """Atualiza o resumo de testes na ordem recebida."""
        self.selection_summary.render(items)

    def set_tests_selected(
        self, selection_ids: Sequence[str], selected_tests: set[str]
    ) -> None:
        """Sincroniza os checkboxes alterados sem reconstruir o catálogo."""
        self.test_catalog.set_tests_selected(selection_ids, selected_tests)

    def set_running(self, running: bool) -> None:
        """Atualiza o controle da execução demonstrativa, se a página existir."""
        if self.winfo_exists():
            self.selection_summary.set_running(running)
            self.client_selector.set_enabled(not running)
            self.test_catalog.set_selection_enabled(not running)

    def set_progress(
        self,
        completed: int | None,
        total: int,
        current_test: str | None,
        duration_seconds: float | None,
    ) -> None:
        """Apresenta o progresso já calculado pelo controlador."""
        if self.winfo_exists():
            self.selection_summary.set_progress(completed, total, current_test, duration_seconds)

    def show_execution_result(self, state: str, message: str) -> None:
        """Mostra o resultado final na área de resumo."""
        if self.winfo_exists():
            self.selection_summary.show_result(state, message)

    def append_log(self, text: str) -> None:
        """Inclui uma linha no painel de logs, se a página existir."""
        if self.winfo_exists():
            self.log_panel.append(text)

    def clear_log(self) -> None:
        """Limpa o buffer visual antes de redesenhar o histórico selecionado."""
        if self.winfo_exists():
            self.log_panel.clear()

    def set_complete_log_mode(self, complete: bool) -> None:
        """Atualiza o rótulo do modo de saída apresentado no painel."""
        if self.winfo_exists():
            self.log_panel.set_complete_mode(complete)

    def set_logs_expanded(self, expanded: bool) -> None:
        """Alterna o layout entre o painel compacto e o ampliado."""
        if not self.winfo_exists():
            return
        self.log_panel.set_expanded(expanded)

    def scroll_to_logs(self) -> None:
        """Mostra o fim da página após uma expansão pedida pelo usuário."""
        if self.winfo_exists():
            self.update_idletasks()
            self._parent_canvas.yview_moveto(1.0)
