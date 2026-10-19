"""Catálogo pesquisável de testes reais."""

from __future__ import annotations

import colorsys
import sys
import unicodedata
from collections.abc import Callable, Iterable, Mapping, Sequence, Set
from dataclasses import dataclass
from functools import lru_cache

import customtkinter as ctk

from gui_v2.components.smart_scrollable_frame import (
    WINDOWS_SCROLL_INCREMENT,
    SmartScrollableFrame,
)
from gui_v2.models.test_item import TestItem
from gui_v2.theme import COLORS


def _normalize(text: str) -> str:
    """Normaliza texto para pesquisa sem caixa e sem acentos."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


_HISTORY_INDICATORS = {
    "pass": ("✔", COLORS["success"]),
    "fail": ("✖", COLORS["error"]),
    "skip": ("⚠", COLORS["orange"]),
}


def _rgb(color: str) -> tuple[int, int, int]:
    """Converte a cor hexadecimal usada pela paleta da GUI para RGB."""
    value = color.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def _blend(color: str, background: str, amount: float) -> str:
    foreground_rgb, background_rgb = _rgb(color), _rgb(background)
    blended = tuple(
        round(fg * amount + bg * (1 - amount))
        for fg, bg in zip(foreground_rgb, background_rgb)
    )
    return _hex(blended)


def _luminance(color: str) -> float:
    channels = [value / 255 for value in _rgb(color)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def _contrasting_module_color(color: str, background: str) -> str:
    """Ajusta apenas a luminosidade, preservando matiz e saturação do módulo."""
    hue, lightness, saturation = colorsys.rgb_to_hls(*(value / 255 for value in _rgb(color)))
    background_luminance = _luminance(background)
    candidates = []
    for step in range(101):
        for target in (0.0, 1.0):
            adjusted = target + (lightness - target) * (1 - step / 100)
            rgb = colorsys.hls_to_rgb(hue, adjusted, saturation)
            candidate = _hex(tuple(round(value * 255) for value in rgb))
            luminance = _luminance(candidate)
            ratio = (max(luminance, background_luminance) + 0.05) / (
                min(luminance, background_luminance) + 0.05
            )
            if ratio >= 4.5:
                candidates.append((abs(adjusted - lightness), candidate))
    return min(candidates)[1] if candidates else color


@lru_cache(maxsize=16)
def _module_button_colors(module_color: str) -> dict[str, tuple[str, str]]:
    """Retorna pares claro/escuro derivados do matiz do módulo e com contraste AA."""
    colors: dict[str, tuple[str, str]] = {}
    backgrounds = COLORS["surface_alt"]
    for key, amount in (
        ("partial", 0.12),
        ("complete", 0.22),
        ("partial_hover", 0.20),
        ("complete_hover", 0.32),
    ):
        colors[key] = tuple(
            _blend(module_color, background, amount) for background in backgrounds
        )
    # Text and borders use the same module hue, with sufficient contrast on every fill.
    colors["text"] = tuple(
        _contrasting_module_color(module_color, _blend(module_color, background, 0.32))
        for background in backgrounds
    )
    return colors


@dataclass(slots=True)
class _CachedModule:
    """Widgets prontos de um módulo para reutilização na mesma página e cliente."""

    frames: list[ctk.CTkFrame]
    variables: dict[str, list[ctk.BooleanVar]]
    indicators: dict[str, list[ctk.CTkLabel]]
    section_buttons: list[tuple[tuple[str, ...], ctk.CTkButton]]


class _CatalogScrollableFrame(SmartScrollableFrame):
    """Aumenta somente a distância de rolagem do catálogo no Windows."""

    def scroll_to_top(self) -> None:
        """Mostra o início do conteúdo após trocar módulo ou filtro."""
        self._parent_canvas.yview_moveto(0.0)

    def _set_scroll_increments(self) -> None:
        if sys.platform.startswith("win"):
            self._parent_canvas.configure(
                xscrollincrement=1, yscrollincrement=WINDOWS_SCROLL_INCREMENT
            )
            return
        super()._set_scroll_increments()


class TestCatalog(ctk.CTkFrame):
    """Mostra, pesquisa e emite alterações do catálogo do módulo ativo."""

    _SEARCH_DELAY_MS = 250

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_test_toggled: Callable[[str, bool], None],
        on_section_toggled: Callable[[tuple[str, ...]], None],
    ) -> None:
        super().__init__(
            master, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"],
        )
        self._on_test_toggled = on_test_toggled
        self._on_section_toggled = on_section_toggled
        self._module = ""
        self._module_color = COLORS["accent_light"]
        self._sections: Mapping[str, Sequence[TestItem]] = {}
        self._selected_tests: Set[str] = set()
        self._history_by_path: Mapping[str, str] = {}
        self._test_variables: dict[str, list[ctk.BooleanVar]] = {}
        self._history_indicators: dict[str, list[ctk.CTkLabel]] = {}
        self._section_buttons: list[tuple[tuple[str, ...], ctk.CTkButton]] = []
        self._cached_modules: dict[str, _CachedModule] = {}
        self._visible_frames: list[ctk.CTkFrame | ctk.CTkLabel] = []
        self._suppress_search_render = False
        self._pending_section_id: str | None = None
        self._pending_search_id: str | None = None
        self._selection_enabled = True
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build()

    def render(
        self,
        module: str,
        module_color: str,
        sections: Mapping[str, Sequence[TestItem]],
        selected_tests: Set[str],
        history_by_path: Mapping[str, str] | None = None,
    ) -> None:
        """Atualiza testes, seleção e resultados de histórico apresentados."""
        self._cancel_pending_search()
        self._module = module
        self._module_color = module_color
        self._sections = sections
        self._selected_tests = selected_tests
        self._history_by_path = history_by_path or {}
        self._module_label.configure(text=module, text_color=module_color)
        self._render_visible_tests()

    def update_history(self, history_by_path: Mapping[str, str]) -> None:
        """Atualiza somente os indicadores, sem reconstruir nem reposicionar o catálogo."""
        self._history_by_path = history_by_path
        for item_path, labels in self._history_indicators.items():
            indicator, color = _HISTORY_INDICATORS.get(
                history_by_path.get(item_path, ""),
                ("•", COLORS["muted"]),
            )
            for label in labels:
                if label.winfo_exists():
                    label.configure(text=indicator, text_color=color)

    def clear_search(self) -> None:
        """Limpa a pesquisa atual antes de trocar o módulo."""
        self._cancel_pending_search()
        if self._search_var.get():
            self._suppress_search_render = True
            try:
                self._search_var.set("")
            finally:
                self._suppress_search_render = False

    def reset_for_client(self) -> None:
        """Descarta widgets do cliente anterior antes de receber outro catálogo."""
        self._cancel_pending_section()
        self._cancel_pending_search()
        self.clear_search()
        for child in self._tests_scroll.winfo_children():
            child.destroy()
        self._cached_modules.clear()
        self._visible_frames.clear()
        self._test_variables = {}
        self._history_indicators = {}
        self._section_buttons = []

    def destroy(self) -> None:
        """Cancela a próxima seção quando a página sai da interface."""
        self._cancel_pending_section()
        self._cancel_pending_search()
        super().destroy()

    def set_tests_selected(
        self, selection_ids: Iterable[str], selected_tests: Set[str]
    ) -> None:
        """Sincroniza somente os checkboxes afetados, sem remontar o catálogo."""
        self._selected_tests = selected_tests
        for selection_id in selection_ids:
            for variable in self._test_variables.get(selection_id, []):
                variable.set(selection_id in selected_tests)
        self._update_section_buttons(selection_ids)

    def _update_section_buttons(self, changed_ids: Iterable[str] | None = None) -> None:
        """Reflete no botão de cada seção os itens selecionados naquele grupo."""
        changed = set(changed_ids) if changed_ids is not None else None
        for selection_ids, button in self._section_buttons:
            if changed is not None and not changed.intersection(selection_ids):
                continue
            selected_count = sum(item_id in self._selected_tests for item_id in selection_ids)
            self._style_section_button(button, selected_count, len(selection_ids))

    def _style_section_button(
        self, button: ctk.CTkButton, selected_count: int, total_count: int
    ) -> None:
        complete = selected_count == total_count
        partial = bool(selected_count) and not complete
        state = "complete" if complete else "partial" if partial else "empty"
        filtered = bool(self._search_var.get().strip())
        text = (
            ("Desmarcar resultados" if filtered else "Desmarcar todos") if complete else
            "Marcar restantes" if partial else ("Marcar resultados" if filtered else "Marcar todos")
        )
        colors = _module_button_colors(self._module_color)
        focused_widget = button.focus_get()
        focused = focused_widget in (button, button._text_label, button._image_label)
        border_width = {"empty": 0, "partial": 2, "complete": 3}[state] + int(focused)
        button.configure(
            text=text,
            fg_color="transparent" if not selected_count else colors[state],
            hover_color=(
                colors[f"{state}_hover"] if state != "empty" else colors["partial_hover"]
            ),
            text_color=colors["text"],
            border_color=colors["text"],
            border_width=border_width,
        )

    def set_selection_enabled(self, enabled: bool) -> None:
        """Bloqueia a seleção nos módulos visíveis e em cache durante o Pytest."""
        self._selection_enabled = enabled
        for child in self._tests_scroll.winfo_children():
            self._set_selection_controls_enabled(child, enabled)

    @classmethod
    def _set_selection_controls_enabled(cls, widget: ctk.CTkBaseClass, enabled: bool) -> None:
        if isinstance(widget, ctk.CTkCheckBox) or (
            isinstance(widget, ctk.CTkButton) and widget.cget("text") in {
                "Marcar todos", "Marcar restantes", "Desmarcar todos",
                "Desmarcar resultados",
            }
        ):
            widget.configure(state="normal" if enabled else "disabled")
        for child in widget.winfo_children():
            cls._set_selection_controls_enabled(child, enabled)

    def _build(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Catálogo de testes", text_color=COLORS["ink"],
                     font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w")
        self._module_label = ctk.CTkLabel(
            top, text="", text_color=COLORS["accent_text"], font=ctk.CTkFont(size=12, weight="bold")
        )
        self._module_label.grid(row=0, column=1)
        self._search_var = ctk.StringVar()
        self._search_var.trace_add(
            "write",
            lambda *_: None if self._suppress_search_render else self._schedule_search(),
        )
        ctk.CTkEntry(
            self, textvariable=self._search_var, height=38, corner_radius=9,
            border_color=COLORS["border"], placeholder_text="⌕  Pesquisar teste pelo nome",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        self._tests_scroll = _CatalogScrollableFrame(self, fg_color="transparent")
        self._tests_scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._tests_scroll.grid_columnconfigure(0, weight=1)

    def _schedule_search(self) -> None:
        """Espera uma pausa na digitação antes de reconstruir o catálogo."""
        self._cancel_pending_search()
        self._pending_search_id = self.after(self._SEARCH_DELAY_MS, self._run_search)

    def _run_search(self) -> None:
        self._pending_search_id = None
        self._render_visible_tests()

    def _cancel_pending_search(self) -> None:
        if self._pending_search_id is not None:
            self.after_cancel(self._pending_search_id)
            self._pending_search_id = None

    def _render_visible_tests(self) -> None:
        self._cancel_pending_section()
        self._tests_scroll.scroll_to_top()
        cached_frames = {
            frame for cached in self._cached_modules.values() for frame in cached.frames
        }
        for child in self._visible_frames:
            if child in cached_frames:
                child.grid_remove()
            else:
                child.destroy()
        self._visible_frames = []
        query = _normalize(self._search_var.get())
        if not query and self._module in self._cached_modules:
            cached = self._cached_modules[self._module]
            self._test_variables = cached.variables
            self._history_indicators = cached.indicators
            self._section_buttons = cached.section_buttons
            for row, frame in enumerate(cached.frames):
                frame.grid(row=row, column=0, sticky="ew", padx=4, pady=5)
            self._visible_frames = list(cached.frames)
            for selection_id, variables in self._test_variables.items():
                selected = selection_id in self._selected_tests
                for variable in variables:
                    if variable.get() != selected:
                        variable.set(selected)
            self.update_history(self._history_by_path)
            self._update_section_buttons()
            return
        self._test_variables = {}
        self._history_indicators = {}
        self._section_buttons = []
        visible_sections: list[tuple[str, list[TestItem]]] = []
        for section, tests in self._sections.items():
            visible = [item for item in tests if query in _normalize(item.name)]
            if visible:
                visible_sections.append((section, visible))
        if not visible_sections:
            empty_label = ctk.CTkLabel(
                self._tests_scroll, text="Nenhum teste encontrado", text_color=COLORS["muted"],
                font=ctk.CTkFont(size=13),
            )
            empty_label.grid(row=0, column=0, pady=50)
            self._visible_frames.append(empty_label)
            return
        if query:
            for row, (section, visible) in enumerate(visible_sections):
                self._append_section(section, visible, row, expanded=True)
            return
        self._append_section(*visible_sections[0], 0)
        if len(visible_sections) == 1:
            self._cache_current_module()
        else:
            self._pending_section_id = self.after(
                16, lambda: self._append_remaining_sections(visible_sections, 1)
            )

    def _cancel_pending_section(self) -> None:
        if self._pending_section_id is not None:
            self.after_cancel(self._pending_section_id)
            self._pending_section_id = None

    def _append_remaining_sections(
        self, sections: list[tuple[str, list[TestItem]]], row: int
    ) -> None:
        self._pending_section_id = None
        self._append_section(*sections[row], row)
        if row + 1 == len(sections):
            self._cache_current_module()
        else:
            self._pending_section_id = self.after(
                16, lambda: self._append_remaining_sections(sections, row + 1)
            )

    def _cache_current_module(self) -> None:
        self._cached_modules[self._module] = _CachedModule(
            list(self._visible_frames), self._test_variables, self._history_indicators,
            self._section_buttons,
        )

    def _append_section(
        self, section: str, visible: list[TestItem], row: int, *, expanded: bool = False
    ) -> None:
        section_frame = ctk.CTkFrame(
            self._tests_scroll, fg_color=COLORS["surface_alt"], corner_radius=10
        )
        section_frame.grid(row=row, column=0, sticky="ew", padx=4, pady=5)
        self._visible_frames.append(section_frame)
        section_frame.grid_columnconfigure(0, weight=1)
        tests_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        tests_frame.grid_columnconfigure(1, weight=1)
        rows_built = False

        def build_rows() -> None:
            """Cria as linhas na primeira expansão: cada CTkCheckBox custa ~2 ms."""
            nonlocal rows_built
            if rows_built:
                return
            rows_built = True
            self._append_test_rows(tests_frame, visible)

        def toggle_section() -> None:
            if tests_frame.winfo_manager():
                tests_frame.grid_remove()
                section_button.configure(text=f"›  {section}")
            else:
                build_rows()
                tests_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                section_button.configure(text=f"▾  {section}")

        section_button = ctk.CTkButton(
            section_frame, text=f"▾  {section}" if expanded else f"›  {section}",
            anchor="w", fg_color="transparent", hover_color=COLORS["border"],
            text_color=COLORS["ink"], font=ctk.CTkFont(size=12, weight="bold"),
            command=toggle_section,
        )
        section_button.grid(row=0, column=0, sticky="ew", padx=(8, 0), pady=6)
        section_ids = tuple(item.selection_id for item in visible)
        filtered = bool(self._search_var.get().strip())
        selection_button = ctk.CTkButton(
            section_frame,
            text="Marcar resultados" if filtered else "Marcar todos",
            width=164 if filtered else 142, height=28, corner_radius=7,
            fg_color="transparent", hover_color=COLORS["border"], text_color=self._module_color,
            border_color=self._module_color, border_width=0,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda items=section_ids: self._on_section_toggled(items),
            state="normal" if self._selection_enabled else "disabled",
        )
        selection_button._text_label.bind(
            "<FocusIn>",
            lambda _event, button=selection_button, total=len(section_ids): self._style_section_button(
                button,
                sum(item_id in self._selected_tests for item_id in section_ids),
                total,
            ),
            add="+",
        )
        selection_button._text_label.bind(
            "<FocusOut>",
            lambda _event, button=selection_button, total=len(section_ids): self._style_section_button(
                button,
                sum(item_id in self._selected_tests for item_id in section_ids),
                total,
            ),
            add="+",
        )
        selection_button.grid(row=0, column=1, padx=10, pady=6)
        self._section_buttons.append((section_ids, selection_button))
        self._update_section_buttons(section_ids)
        if expanded:
            build_rows()
            tests_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _append_test_rows(
        self, tests_frame: ctk.CTkFrame, visible: list[TestItem]
    ) -> None:
        """Cria indicador e checkbox com a seleção e o histórico atuais.

        Seções ainda não construídas não têm variáveis registradas; por isso
        os valores iniciais vêm do estado vigente no momento da expansão.
        """
        for index, item in enumerate(visible, start=1):
            variable = ctk.BooleanVar(value=item.selection_id in self._selected_tests)
            self._test_variables.setdefault(item.selection_id, []).append(variable)
            indicator, indicator_color = _HISTORY_INDICATORS.get(
                self._history_by_path.get(item.path, ""),
                ("•", COLORS["muted"]),
            )
            indicator_label = ctk.CTkLabel(
                tests_frame, text=indicator, width=18, text_color=indicator_color,
                font=ctk.CTkFont(size=12, weight="bold"),
            )
            indicator_label.grid(
                row=index, column=0, sticky="w", padx=(14, 2),
                pady=(2, 7 if index == len(visible) else 2),
            )
            self._history_indicators.setdefault(item.path, []).append(indicator_label)
            checkbox = ctk.CTkCheckBox(
                tests_frame, text=item.name, variable=variable, height=28, corner_radius=5,
                checkbox_width=20, checkbox_height=20, border_width=2,
                fg_color=COLORS["accent_fill"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["ink"], font=ctk.CTkFont(size=11),
                command=lambda var=variable, selection_id=item.selection_id: self._on_test_toggled(selection_id, var.get()),
                state="normal" if self._selection_enabled else "disabled",
            )
            checkbox.grid(
                row=index, column=1, sticky="w", padx=(2, 14),
                pady=(2, 7 if index == len(visible) else 2),
            )
