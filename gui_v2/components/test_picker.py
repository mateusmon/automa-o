"""Seletor pesquisável de testes específicos disponíveis para a Sentinela."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from tkinter import StringVar
import unicodedata

import customtkinter as ctk

from gui_v2.components.popup_geometry import position_popup
from gui_v2.components.picker_results import PickerResults
from gui_v2.models.test_item import TestItem
from gui_v2.theme import COLORS


def _normalize(value: str) -> str:
    """Normaliza caixa e acentos para buscas tolerantes."""
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(character for character in decomposed if unicodedata.category(character) != "Mn")


class TestPicker(ctk.CTkFrame):
    """Escolhe um teste pelo nome ou path em uma lista flutuante pesquisável."""

    _ROW_HEIGHT = 42
    _MAX_VISIBLE_ROWS = 10
    _MIN_WIDTH = 420
    _SEARCH_HEIGHT = 50
    _RESULTS_INSET = 18  # raio 8 + borda 1 em cima e embaixo
    _EMPTY_RESULTS_HEIGHT = 48
    _MAX_RESULTS = 30
    _SEARCH_DELAY_MS = 250

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        items: Sequence[TestItem],
        on_selected: Callable[[str], None],
        width: int = 520,
        placeholder: str = "Selecione um teste",
        show_selected_item: bool = True,
        on_multi_toggle: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(master, fg_color="transparent", width=width, height=36)
        self._items: tuple[TestItem, ...] = ()
        self._items_by_id: dict[str, TestItem] = {}
        self._selected_item: TestItem | None = None
        self._on_selected = on_selected
        self._placeholder = placeholder
        self._show_selected_item = show_selected_item
        self._on_multi_toggle = on_multi_toggle
        self._multi_selected_ids: set[str] = set()
        self._result_buttons: list[ctk.CTkButton] = []
        self._enabled = True
        self._popup: ctk.CTkToplevel | None = None
        self._popup_above = False
        self._search_var: StringVar | None = None
        self._results: ctk.CTkScrollableFrame | None = None
        self._matches: tuple[TestItem, ...] = ()
        self._highlighted_index: int | None = None
        self._pending_search_id: str | None = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._button = ctk.CTkButton(
            self,
            text=self._placeholder,
            anchor="w",
            height=36,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_alt"],
            text_color=COLORS["ink"],
            command=self.open,
        )
        self._button.grid(row=0, column=0, sticky="ew")
        self.set_items(items)

    @property
    def selected_item(self) -> TestItem | None:
        """Retorna o teste confirmado, sem considerar o destaque temporário da busca."""
        return self._selected_item

    def set_enabled(self, enabled: bool) -> None:
        """Bloqueia alterações enquanto a Sentinela está em execução."""
        self._enabled = enabled
        self._button.configure(state="normal" if enabled else "disabled")
        if not enabled:
            self.close()

    def set_items(self, items: Sequence[TestItem]) -> None:
        """Substitui o catálogo pelo conjunto elegível para o cliente atual."""
        self.close()
        self._items = tuple(items)
        self._items_by_id = {item.selection_id: item for item in self._items}
        self.set_selected_item(None)

    def set_selected_item(self, item: TestItem | None) -> None:
        """Atualiza somente a seleção confirmada e o rótulo do botão."""
        self._selected_item = (
            self._items_by_id.get(item.selection_id)
            if item is not None
            else None
        )
        self._refresh_label()
        self._refresh_result_buttons()

    def set_multi_selected_items(self, selection_ids: Sequence[str]) -> None:
        """Sincroniza as marcas múltiplas confirmadas pelo controlador."""
        self._multi_selected_ids = set(selection_ids)
        self._refresh_result_buttons()

    def _refresh_result_buttons(self) -> None:
        for index in range(min(len(self._result_buttons), len(self._matches))):
            self._style_result_button(index)

    def open(self) -> None:
        """Abre a busca e mostra no máximo dez linhas com rolagem."""
        if not self._enabled:
            return
        if self._popup is not None and self._popup.winfo_exists():
            self.close()
            return

        self.update_idletasks()
        initial_rows = min(max(min(len(self._items), self._MAX_RESULTS), 1), self._MAX_VISIBLE_ROWS)
        initial_results_height = max(
            initial_rows * self._ROW_HEIGHT,
            self._EMPTY_RESULTS_HEIGHT if not self._items else 0,
        )
        popup_height = (
            self._SEARCH_HEIGHT + self._RESULTS_INSET + initial_results_height
        )
        popup_width = max(self.winfo_width(), self._MIN_WIDTH)
        position = position_popup(self, popup_width, popup_height)
        popup_width = position.width
        popup_height = position.height
        self._popup_above = position.above

        popup = ctk.CTkToplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.transient(self.winfo_toplevel())
        popup.configure(fg_color=COLORS["surface"])
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=1)
        popup.bind("<Down>", self._move_highlight)
        popup.bind("<Up>", self._move_highlight)
        popup.bind("<Return>", self._confirm_highlight)
        popup.bind("<Escape>", self._cancel)
        popup.bind("<Tab>", self._cancel)
        popup.bind("<FocusOut>", self._on_focus_out)

        self._search_var = StringVar(master=popup, value="")
        self._search_var.trace_add("write", lambda *_args: self._schedule_search())
        search_entry = ctk.CTkEntry(
            popup,
            textvariable=self._search_var,
            height=34,
            corner_radius=8,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
            text_color=COLORS["ink"],
            placeholder_text="Pesquisar nome ou caminho",
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        search_entry.bind("<Down>", self._move_highlight)
        search_entry.bind("<Up>", self._move_highlight)
        search_entry.bind("<Return>", self._confirm_highlight)
        search_entry.bind("<Escape>", self._cancel)
        search_entry.bind("<Tab>", self._cancel)
        results = PickerResults(
            popup,
            width=popup_width - 14,
            height=initial_results_height,
            fg_color=COLORS["surface"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        results.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))
        results.grid_columnconfigure(0, weight=1)
        self._popup = popup
        self._results = results
        self._render_results()
        popup.geometry(f"{popup_width}x{popup_height}+{position.x}+{position.y}")
        popup.deiconify()
        popup.lift()
        popup.after_idle(lambda: self._focus_popup(popup, search_entry))

    def _focus_popup(self, popup: ctk.CTkToplevel, entry: ctk.CTkEntry) -> None:
        """Entrega o foco à busca depois de a janela flutuante estar mapeada."""
        if self._popup is popup and popup.winfo_exists():
            entry.focus_force()

    def _render_results(self) -> None:
        """Filtra pelo nome e path sem alterar a seleção confirmada."""
        results = self._results
        if results is None or not results.winfo_exists():
            return
        for child in results.winfo_children():
            child.destroy()
        self._result_buttons.clear()
        results.reset_scroll()

        query = _normalize(self._search_var.get().strip()) if self._search_var else ""
        all_matches = tuple(
            item
            for item in self._items
            if not query
            or query in _normalize(item.name)
            or query in _normalize(item.path)
        )
        previous_id = (
            self._matches[self._highlighted_index].selection_id
            if self._highlighted_index is not None
            and self._highlighted_index < len(self._matches)
            else None
        )
        matches = all_matches[:self._MAX_RESULTS]
        self._matches = matches
        self._highlighted_index = next(
            (
                index
                for index, item in enumerate(matches)
                if item.selection_id == previous_id
            ),
            0 if matches else None,
        )
        visible_rows = min(max(len(matches), 1), self._MAX_VISIBLE_ROWS)
        results_height = max(
            visible_rows * self._ROW_HEIGHT,
            self._EMPTY_RESULTS_HEIGHT if not matches else 0,
        )
        results.configure(height=results_height)
        popup = self._popup
        if popup is not None and popup.winfo_exists():
            popup_height = self._SEARCH_HEIGHT + self._RESULTS_INSET + results_height
            position = position_popup(self, popup.winfo_width(), popup_height)
            self._popup_above = position.above
            popup.geometry(
                f"{position.width}x{position.height}"
                f"+{position.x}+{position.y}"
            )
        if not matches:
            ctk.CTkLabel(
                results,
                text="Nenhum teste encontrado",
                anchor="w",
                text_color=COLORS["muted"],
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=10)
            return

        for row, item in enumerate(matches):
            highlighted = row == self._highlighted_index
            confirmed = self._is_confirmed(item)
            label = f"{item.name} · {item.path}"
            button = ctk.CTkButton(
                results,
                text=("✓  " if confirmed else "□  ") + label
                if self._on_multi_toggle is not None else label,
                anchor="w",
                height=self._ROW_HEIGHT - 2,
                corner_radius=6,
                fg_color=COLORS["accent_selected"] if highlighted else "transparent",
                hover_color=COLORS["surface_alt"],
                border_width=1 if highlighted else 0,
                border_color=COLORS["accent_text"],
                text_color=COLORS["accent_text"] if highlighted else COLORS["ink"],
                command=lambda selected_id=item.selection_id: self._choose(selected_id),
            )
            button.grid(row=row, column=0, sticky="ew", padx=4, pady=1)
            button.bind("<Enter>", lambda _event, index=row: self._set_highlight(index))
            self._result_buttons.append(button)
        if len(all_matches) > self._MAX_RESULTS:
            ctk.CTkLabel(
                results,
                text=f"Mostrando {self._MAX_RESULTS} de {len(all_matches)} · refine a pesquisa",
                text_color=COLORS["muted"],
                anchor="w",
            ).grid(row=len(matches), column=0, sticky="ew", padx=12, pady=6)

    def _schedule_search(self) -> None:
        """Atualiza os resultados quando a digitação fizer uma pausa."""
        popup = self._popup
        if popup is None or not popup.winfo_exists():
            return
        if self._pending_search_id is not None:
            popup.after_cancel(self._pending_search_id)
        self._pending_search_id = popup.after(self._SEARCH_DELAY_MS, self._run_search)

    def _run_search(self) -> None:
        self._pending_search_id = None
        self._render_results()

    def _set_highlight(self, index: int) -> None:
        """Move o destaque temporário sem confirmar a seleção."""
        if index < 0 or index >= len(self._matches) or index == self._highlighted_index:
            return
        results = self._results
        if results is None:
            return
        previous = self._highlighted_index
        self._highlighted_index = index
        if previous is not None:
            self._style_result_button(previous)
        self._style_result_button(index)

    def _style_result_button(self, index: int) -> None:
        if index < 0 or index >= len(self._result_buttons) or index >= len(self._matches):
            return
        button = self._result_buttons[index]
        highlighted = index == self._highlighted_index
        selected = self._is_confirmed(self._matches[index])
        button.configure(
            text=("✓  " if selected else "□  ")
            + f"{self._matches[index].name} · {self._matches[index].path}",
            fg_color=COLORS["accent_selected"] if highlighted else "transparent",
            border_width=1 if highlighted or selected else 0,
            border_color=COLORS["accent_text"] if highlighted or selected else COLORS["border"],
            text_color=COLORS["accent_text"] if highlighted or selected else COLORS["ink"],
        )

    def _is_confirmed(self, item: TestItem) -> bool:
        return (
            self._on_multi_toggle is not None
            and item.selection_id in self._multi_selected_ids
        ) or (
            self._selected_item is not None
            and item.selection_id == self._selected_item.selection_id
        )

    def _choose(self, selection_id: str) -> None:
        """Alterna marca no modo múltiplo ou confirma no modo simples."""
        if self._on_multi_toggle is None:
            self._confirm(selection_id)
            return
        if not self._enabled:
            return
        self._on_multi_toggle(selection_id)

    def _move_highlight(self, event: object) -> str:
        """Percorre ciclicamente a lista e mantém o resultado visível."""
        if self._pending_search_id is not None and self._popup is not None:
            self._popup.after_cancel(self._pending_search_id)
            self._run_search()
        if not self._matches:
            return "break"
        direction = -1 if getattr(event, "keysym", "") == "Up" else 1
        current = self._highlighted_index
        if current is None:
            current = 0 if direction > 0 else len(self._matches) - 1
        else:
            current = (current + direction) % len(self._matches)
        self._set_highlight(current)
        if self._results is not None:
            self._results.reveal(current)
        return "break"

    def _confirm_highlight(self, _event: object) -> str:
        """Confirma apenas o resultado destacado, quando há correspondências."""
        if self._pending_search_id is not None:
            self._popup.after_cancel(self._pending_search_id)
            self._run_search()
        if self._highlighted_index is not None and self._matches:
            self._choose(self._matches[self._highlighted_index].selection_id)
        return "break"

    def _cancel(self, _event: object = None) -> str:
        """Fecha a pesquisa sem alterar o teste confirmado."""
        self.close()
        return "break"

    def _on_focus_out(self, _event: object) -> None:
        """Fecha o popup quando o foco deixa a janela flutuante."""
        popup = self._popup
        if popup is None or not popup.winfo_exists():
            return
        popup.after_idle(lambda: self._close_if_unfocused(popup))

    def _close_if_unfocused(self, popup: ctk.CTkToplevel) -> None:
        """Reavalia o foco após a transição, sem fechar um popup reaberto."""
        if self._popup is not popup or not popup.winfo_exists():
            return
        focused = popup.focus_get()
        if focused is None or focused.winfo_toplevel() is not popup:
            self.close()

    def close(self) -> None:
        """Fecha e descarta somente o estado temporário da busca."""
        popup, self._popup = self._popup, None
        if popup is not None and self._pending_search_id is not None:
            popup.after_cancel(self._pending_search_id)
        self._pending_search_id = None
        self._search_var = None
        self._results = None
        self._matches = ()
        self._result_buttons.clear()
        self._highlighted_index = None
        self._popup_above = False
        if popup is not None and popup.winfo_exists():
            popup.destroy()

    def destroy(self) -> None:
        """Remove o popup ao reconstruir os módulos ou fechar a página."""
        self.close()
        super().destroy()

    def _confirm(self, selection_id: str) -> None:
        item = self._items_by_id.get(selection_id)
        if item is None or not self._enabled:
            self.close()
            return
        self._selected_item = item
        self._refresh_label()
        self.close()
        self._on_selected(item.selection_id)

    def _refresh_label(self) -> None:
        item = self._selected_item
        if item is not None and not self._show_selected_item:
            label = f"✓ {self._placeholder}"
        elif item is not None:
            label = f"{item.name} · {item.path}"
        else:
            label = self._placeholder
        self._button.configure(
            text=label
        )
