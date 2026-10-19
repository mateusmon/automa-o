"""Resumo visual da seleção de testes demonstrativos."""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence

import customtkinter as ctk

from gui_v2.components.smart_scrollable_frame import (
    WINDOWS_SCROLL_INCREMENT,
    SmartScrollableFrame,
)
from gui_v2.theme import COLORS


def _format_duration(seconds: float) -> str:
    """Formata duração já medida pelo controlador em mm:ss ou hh:mm:ss."""
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds_part = divmod(remainder, 60)
    return f"{hours}:{minutes:02}:{seconds_part:02}" if hours else f"{minutes:02}:{seconds_part:02}"


class SelectionSummary(ctk.CTkFrame):
    """Exibe a seleção na ordem recebida e controla a execução demonstrativa."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_run: Callable[[], None],
        on_stop: Callable[[], None],
        on_clear_selection: Callable[[], None],
    ) -> None:
        super().__init__(
            master, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"],
        )
        self._on_run = on_run
        self._on_stop = on_stop
        self._on_clear_selection = on_clear_selection
        self._running = False
        self._selection_count = 0
        self._rendered_items: list[tuple[str, str]] = []
        self._expanded_modules: set[str] = set()
        self._module_rows: dict[str, tuple[ctk.CTkButton, ctk.CTkFrame]] = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self._build()

    def render(self, items: Sequence[tuple[str, str]]) -> None:
        """Mostra os testes selecionados, já ordenados pelo catálogo."""
        previous_modules = {module for _, module in self._rendered_items}
        self._rendered_items = list(items)
        count = len(items)
        self._selection_count = count
        self._selection_label.configure(
            text=f"{count} teste{'s' if count != 1 else ''} selecionado{'s' if count != 1 else ''}"
        )
        self._clear_selection_button.configure(
            state="normal" if count and not self._running else "disabled"
        )
        for child in self._selection_box.winfo_children():
            child.destroy()
        self._module_rows.clear()
        if not items:
            self._expanded_modules.clear()
            ctk.CTkLabel(
                self._selection_box, text="Sua seleção aparecerá aqui, na ordem do catálogo.",
                anchor="w", text_color=COLORS["muted"], font=ctk.CTkFont(size=11),
            ).grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        else:
            grouped: dict[str, list[str]] = {}
            for test, module in items:
                grouped.setdefault(module, []).append(test)
            self._expanded_modules.update(set(grouped) - previous_modules)
            self._expanded_modules.intersection_update(grouped)
            for index, (module, tests) in enumerate(grouped.items()):
                self._render_module(module, tests, index * 2)

    def _render_module(self, module: str, tests: Sequence[str], row: int) -> None:
        """Cria um cabeçalho expansível e a lista indentada de testes do módulo."""
        expanded = module in self._expanded_modules
        toggle = ctk.CTkButton(
            self._selection_box, text=f"{'▾' if expanded else '›'}  {module}", anchor="w",
            height=26, fg_color="transparent", hover_color=COLORS["border"],
            text_color=COLORS["ink"], font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._toggle_module(module),
        )
        toggle.grid(row=row, column=0, sticky="ew", padx=4, pady=(2, 0))
        tests_frame = ctk.CTkFrame(self._selection_box, fg_color="transparent")
        tests_frame.grid(row=row + 1, column=0, sticky="ew")
        tests_frame.grid_columnconfigure(0, weight=1)
        if expanded:
            for index, test in enumerate(tests):
                ctk.CTkLabel(
                    tests_frame, text=f"• {test}", anchor="w", text_color=COLORS["ink"],
                    font=ctk.CTkFont(size=11),
                ).grid(row=index, column=0, sticky="ew", padx=(22, 4), pady=1)
        else:
            tests_frame.grid_remove()
        self._module_rows[module] = (toggle, tests_frame)

    def _toggle_module(self, module: str) -> None:
        """Expande ou recolhe os testes de um módulo."""
        if module in self._expanded_modules:
            self._expanded_modules.remove(module)
        else:
            self._expanded_modules.add(module)
        toggle, tests_frame = self._module_rows[module]
        expanded = module in self._expanded_modules
        toggle.configure(text=f"{'▾' if expanded else '›'}  {module}")
        if expanded:
            tests_frame.grid()
        else:
            tests_frame.grid_remove()

    def set_progress(
        self,
        completed: int | None,
        total: int,
        current_test: str | None,
        duration_seconds: float | None,
    ) -> None:
        """Exibe apenas progresso e duração sustentados por eventos reconhecidos."""
        if completed is None:
            self._progress_label.configure(text="Progresso indisponível")
            self._progress_bar.set(0)
        else:
            self._progress_label.configure(text=f"Progresso  {completed}/{total}")
            self._progress_bar.set(min(1.0, completed / total) if total else 0)
        self._current_test_label.configure(text=f"Atual: {current_test or '—'}")
        duration_text = "—" if duration_seconds is None else _format_duration(duration_seconds)
        self._duration_label.configure(text=f"Duração: {duration_text}")

    def show_result(self, state: str, message: str) -> None:
        """Apresenta o resultado final sem modal nem interrupção do fluxo."""
        colors = {
            "SUCCEEDED": COLORS["success"],
            "SKIPPED": COLORS["orange"],
            "FAILED": COLORS["error"],
            "INTERRUPTED": COLORS["muted"],
        }
        self._result_label.configure(text=message, text_color=colors.get(state, COLORS["muted"]))

    def set_running(self, running: bool) -> None:
        """Alterna o botão entre iniciar e interromper a demonstração."""
        self._running = running
        self._clear_selection_button.configure(
            state="disabled" if running or not self._selection_count else "normal"
        )
        self._run_button.configure(
            text="■  Parar execução" if running else "▶  Executar testes",
            fg_color=COLORS["error_fill"] if running else COLORS["accent_fill"],
            hover_color=COLORS["error_hover"] if running else COLORS["accent_hover"],
            command=self._on_stop if running else self._on_run,
        )

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Sua execução", text_color=COLORS["ink"],
                     font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 3))
        self._selection_label = ctk.CTkLabel(
            self, text="0 testes selecionados", text_color=COLORS["muted"], anchor="w"
        )
        self._selection_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18)
        self._clear_selection_button = ctk.CTkButton(
            self, text="Limpar seleção", width=100, height=26, corner_radius=7,
            fg_color="transparent", hover_color=COLORS["border"],
            text_color=COLORS["accent_text"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_clear_selection, state="disabled",
        )
        self._clear_selection_button.grid(row=2, column=0, columnspan=2, sticky="e", padx=18)
        self._selection_box = SmartScrollableFrame(
            self, height=100, corner_radius=9, fg_color=COLORS["surface_alt"],
            scrollbar_button_color=COLORS["border"],
        )
        if sys.platform.startswith("win"):
            self._selection_box._parent_canvas.configure(
                xscrollincrement=1, yscrollincrement=WINDOWS_SCROLL_INCREMENT
            )
        self._selection_box.grid_columnconfigure(0, weight=1)
        self._selection_box.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=18, pady=(8, 14))
        self._progress_label = ctk.CTkLabel(self, text="Progresso indisponível", text_color=COLORS["muted"], anchor="w")
        self._progress_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 4))
        self._progress_bar = ctk.CTkProgressBar(self, height=8, progress_color=COLORS["accent_fill"])
        self._progress_bar.grid(row=5, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8))
        self._progress_bar.set(0)
        self._current_test_label = ctk.CTkLabel(
            self, text="Atual: —", text_color=COLORS["muted"], anchor="w", wraplength=240, justify="left"
        )
        self._current_test_label.grid(row=6, column=0, columnspan=2, sticky="ew", padx=18, pady=2)
        self._duration_label = ctk.CTkLabel(self, text="Duração: —", text_color=COLORS["muted"], anchor="w")
        self._duration_label.grid(row=7, column=0, columnspan=2, sticky="ew", padx=18, pady=(2, 8))
        self._result_label = ctk.CTkLabel(
            self, text="", text_color=COLORS["muted"], anchor="w", wraplength=240, justify="left"
        )
        self._result_label.grid(row=8, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8))
        self._run_button = ctk.CTkButton(
            self, text="▶  Executar testes", height=44, corner_radius=10,
            fg_color=COLORS["accent_fill"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"), command=self._on_run,
        )
        self._run_button.grid(row=9, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))
