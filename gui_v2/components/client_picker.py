"""Seletor reutilizável de clientes para as páginas da GUI v2."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from tkinter import StringVar, TclError

import customtkinter as ctk

from gui_v2.components.popup_geometry import position_popup
from gui_v2.components.picker_results import PickerResults
from gui_v2.theme import COLORS


class _PickerComboBox(ctk.CTkComboBox):
    """Usa a aparência do combo padrão com o popup do seletor."""

    def __init__(self, *args: object, on_open: Callable[[], None], **kwargs: object) -> None:
        self._on_open = on_open
        super().__init__(*args, **kwargs)

    def _open_dropdown_menu(self) -> None:
        self._on_open()


class ClientPicker(ctk.CTkFrame):
    """Escolhe uma chave numa lista flutuante, com pesquisa opcional."""

    _ROW_HEIGHT = 38
    _MAX_VISIBLE_ROWS = 10
    _MIN_WIDTH = 240
    _SEARCH_HEIGHT = 50
    _RESULTS_INSET = 18  # raio 8 + borda 1 em cima e embaixo
    _SCROLLABLE_FRAME_INSET = 8  # área usada pelo frame/scrollbar interno
    _EMPTY_RESULTS_HEIGHT = 48

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        clients: Mapping[str, str],
        active_client_key: str,
        on_selected: Callable[[str], None],
        width: int = 240,
        searchable: bool = True,
        max_visible_rows: int = _MAX_VISIBLE_ROWS,
    ) -> None:
        super().__init__(master, fg_color="transparent", width=width, height=36)
        if not clients:
            raise ValueError("O seletor de clientes precisa de ao menos um cliente.")
        if active_client_key not in clients:
            raise KeyError(f"Cliente ativo não encontrado: {active_client_key}")
        if type(max_visible_rows) is not int or max_visible_rows < 1:
            raise ValueError("O limite visível precisa ser um inteiro positivo.")

        self._clients = tuple(clients.items())
        self._searchable = searchable
        self._max_visible_rows = max_visible_rows
        self._display_by_key = (
            self._build_display_names(self._clients)
            if searchable else dict(self._clients)
        )
        self._active_client_key = active_client_key
        self._on_selected = on_selected
        self._enabled = True
        self._popup: ctk.CTkToplevel | None = None
        self._popup_bindings: list[tuple[str, str]] = []
        self._popup_above = False
        self._search_var: StringVar | None = None
        self._results: ctk.CTkScrollableFrame | ctk.CTkFrame | None = None
        self._search_entry: ctk.CTkEntry | None = None
        self._matches: tuple[tuple[str, str], ...] = ()
        self._highlighted_index: int | None = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._button = _PickerComboBox(
            self,
            values=[""],
            height=36,
            corner_radius=8,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
            button_color=COLORS["surface_alt"],
            button_hover_color=COLORS["border"],
            text_color=COLORS["ink"],
            state="readonly",
            on_open=self.open,
        )
        self._button.grid(row=0, column=0, sticky="ew")
        self._button.bind("<Button-1>", self._open_from_field)
        self._refresh_label()

    def _open_from_field(self, _event: object) -> str:
        """Abre a pesquisa sem deixar o campo somente leitura recuperar o foco."""
        self.open()
        return "break"

    @staticmethod
    def _build_display_names(clients: tuple[tuple[str, str], ...]) -> dict[str, str]:
        """Inclui a chave nos rótulos e resolve qualquer colisão de exibição."""
        labels: dict[str, str] = {}
        used: set[str] = set()
        for key, label in clients:
            display = f"{label or key} ({key})"
            while display in used:
                display += " ·"
            labels[key] = display
            used.add(display)
        return labels

    @property
    def active_client_key(self) -> str:
        """Chave do cliente atualmente confirmado pelo controlador."""
        return self._active_client_key

    def set_active_client(self, client_key: str) -> None:
        """Atualiza a apresentação após o controlador aceitar uma troca."""
        if client_key not in self._display_by_key:
            raise KeyError(f"Cliente não encontrado no seletor: {client_key}")
        self._active_client_key = client_key
        self._refresh_label()

    def set_options(self, options: Mapping[str, str], active_key: str) -> None:
        """Substitui as opções e atualiza a opção apresentada sem emitir callback."""
        if not options:
            raise ValueError("O seletor precisa de ao menos uma opção.")
        if active_key not in options:
            raise KeyError(f"Opção ativa não encontrada no seletor: {active_key}")
        self.close()
        self._clients = tuple(options.items())
        self._display_by_key = (
            self._build_display_names(self._clients)
            if self._searchable else dict(self._clients)
        )
        self._active_client_key = active_key
        self._refresh_label()

    def set_enabled(self, enabled: bool) -> None:
        """Bloqueia a abertura da lista durante uma execução."""
        self._enabled = enabled
        self._button.configure(state="readonly" if enabled else "disabled")
        if not enabled:
            self.close()

    def open(self) -> None:
        """Abre a lista com a quantidade de linhas visíveis configurada."""
        if not self._enabled:
            return
        if self._popup is not None and self._popup.winfo_exists():
            self.close()
            return

        self.update_idletasks()
        visible_rows = min(max(len(self._clients), 1), self._max_visible_rows)
        results_height = (
            visible_rows * self._ROW_HEIGHT + self._SCROLLABLE_FRAME_INSET
        )
        search_height = self._SEARCH_HEIGHT if self._searchable else 0
        popup_height = search_height + self._RESULTS_INSET + results_height
        popup_width = max(self.winfo_width(), self._MIN_WIDTH if self._searchable else 0)
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
        popup.grid_rowconfigure(1 if self._searchable else 0, weight=1)
        popup.bind("<Escape>", self._cancel)
        popup.bind("<Down>", self._move_highlight)
        popup.bind("<Up>", self._move_highlight)
        popup.bind("<Return>", self._confirm_highlight)
        popup.bind("<Tab>", self._cancel)
        popup.bind("<FocusOut>", self._on_focus_out)

        search_entry = None
        if self._searchable:
            self._search_var = StringVar(master=popup, value="")
            self._search_var.trace_add("write", lambda *_args: self._render_results())
            search_entry = ctk.CTkEntry(
                popup,
                textvariable=self._search_var,
                height=34,
                corner_radius=8,
                border_color=COLORS["border"],
                fg_color=COLORS["surface"],
                text_color=COLORS["ink"],
                placeholder_text="Pesquisar nome ou chave",
            )
            search_entry.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
            search_entry.bind("<Down>", self._move_highlight)
            search_entry.bind("<Up>", self._move_highlight)
            search_entry.bind("<Return>", self._confirm_highlight)
            search_entry.bind("<Escape>", self._cancel)
            search_entry.bind("<Tab>", self._cancel)
            results = PickerResults(
                popup, width=popup_width - 14, height=results_height,
                fg_color=COLORS["surface"], corner_radius=8,
                border_width=1, border_color=COLORS["border"],
            )
            results.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))
        else:
            results = PickerResults(
                popup, width=popup_width - 14, height=results_height,
                fg_color=COLORS["surface"], corner_radius=8,
                border_width=1, border_color=COLORS["border"],
            )
            results.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        results.grid_columnconfigure(0, weight=1)
        self._results = results
        self._search_entry = search_entry
        self._render_results()

        popup.geometry(f"{popup_width}x{popup_height}+{position.x}+{position.y}")
        popup.deiconify()
        popup.lift()
        self._popup = popup
        self._bind_popup_dismissal(popup)
        popup.after_idle(lambda: self._focus_popup(popup, search_entry))

    def _bind_popup_dismissal(self, popup: ctk.CTkToplevel) -> None:
        """Fecha a lista se a janela hospedeira rolar ou receber outro clique."""
        host_scrollable = self._host_scrollable()
        if host_scrollable is None:
            return
        sequences = ("<MouseWheel>", "<Button-4>", "<Button-5>", "<ButtonPress-1>")
        for sequence in sequences:
            binding_id = host_scrollable.bind_all(
                sequence,
                lambda event, current_popup=popup, current_sequence=sequence: (
                    self._dismiss_popup_on_host_interaction(
                        event, current_popup, current_sequence
                    )
                ),
                add="+",
            )
            if binding_id:
                self._popup_bindings.append((sequence, binding_id))

    def _host_scrollable(self) -> ctk.CTkScrollableFrame | None:
        """Localiza a página rolável que contém este seletor."""
        current = self.master
        while current is not None:
            if isinstance(current, ctk.CTkScrollableFrame):
                return current
            current = getattr(current, "master", None)
        return None

    def _dismiss_popup_on_host_interaction(
        self, event: object, popup: ctk.CTkToplevel, sequence: str
    ) -> None:
        """Não deixa popup flutuante se separar do campo durante a rolagem."""
        if self._popup is not popup or not popup.winfo_exists():
            return
        widget = getattr(event, "widget", None)
        if widget is None:
            return
        try:
            if widget.winfo_toplevel() is popup:
                if sequence == "<ButtonPress-1>":
                    return
                if self._is_inside_picker_results(widget):
                    return
                self.close()
                return
        except (AttributeError, TclError):
            return
        if sequence == "<ButtonPress-1>":
            if self._is_inside_picker(widget):
                return
            self.close()
        elif self._is_host_scroll_event(widget):
            self.close()

    def _is_host_scroll_event(self, widget: object) -> bool:
        """Aceita apenas eventos na região rolável que contém o seletor."""
        host_scrollable = self._host_scrollable()
        if host_scrollable is None:
            return False
        host_canvas = getattr(host_scrollable, "_parent_canvas", None)
        host_scrollbar = getattr(host_scrollable, "_scrollbar", None)
        scrollbar_canvas = getattr(host_scrollbar, "_canvas", None)
        current = widget
        while current is not None:
            if current in (
                host_scrollable, host_canvas, host_scrollbar, scrollbar_canvas
            ):
                return True
            if (
                current is not widget
                and isinstance(current, ctk.CTkScrollableFrame)
            ):
                return False
            current = getattr(current, "master", None)
        return False

    def _is_inside_picker(self, widget: object) -> bool:
        """Identifica o clique inicial no campo ou na seta deste seletor."""
        current = widget
        while current is not None:
            if current is self:
                return True
            current = getattr(current, "master", None)
        return False

    def _is_inside_picker_results(self, widget: object) -> bool:
        """Preserva a rolagem da lista interna do seletor pesquisável."""
        results = self._results
        if not isinstance(results, PickerResults):
            return False
        results_scrollbar = results._scrollbar
        results_widgets = (
            results, results._parent_canvas,
            results_scrollbar, results_scrollbar._canvas,
        )
        current = widget
        while current is not None:
            if current in results_widgets:
                return True
            current = getattr(current, "master", None)
        return False

    def _focus_popup(
        self, popup: ctk.CTkToplevel, search_entry: ctk.CTkEntry | None
    ) -> None:
        """Entrega o foco após o clique do campo ou da seta terminar."""
        if self._popup is popup and popup.winfo_exists():
            (search_entry or self._results.winfo_children()[0]).focus_force()

    def _render_results(self) -> None:
        """Filtra por nome ou chave sem confirmar alterações de cliente."""
        results = self._results
        if results is None or not results.winfo_exists():
            return
        for child in results.winfo_children():
            child.destroy()
        if isinstance(results, PickerResults):
            results.reset_scroll()

        query = self._search_var.get().strip().casefold() if self._search_var else ""
        matches = tuple(
            (key, label)
            for key, label in self._clients
            if not query
            or query in label.casefold()
            or query in key.casefold()
        )
        previous_key = (
            self._matches[self._highlighted_index][0]
            if self._highlighted_index is not None
            and self._highlighted_index < len(self._matches)
            else None
        )
        self._matches = matches
        self._highlighted_index = (
            next(
                (index for index, (key, _label) in enumerate(matches) if key == previous_key),
                0 if matches else None,
            )
        )
        visible_rows = min(max(len(matches), 1), self._max_visible_rows)
        results_height = max(
            visible_rows * self._ROW_HEIGHT,
            self._EMPTY_RESULTS_HEIGHT if not matches else 0,
        ) + self._SCROLLABLE_FRAME_INSET
        results.configure(height=results_height)
        popup = self._popup
        if popup is not None and popup.winfo_exists():
            popup_height = (
                (self._SEARCH_HEIGHT if self._searchable else 0)
                + self._RESULTS_INSET + results_height
            )
            position = position_popup(self, popup.winfo_width(), popup_height)
            self._popup_above = position.above
            popup.geometry(
                f"{position.width}x{position.height}"
                f"+{position.x}+{position.y}"
            )
        if not matches:
            ctk.CTkLabel(
                results,
                text="Nenhum cliente encontrado",
                anchor="w",
                text_color=COLORS["muted"],
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=10)
            return

        for row, (key, _label) in enumerate(matches):
            active = key == self._active_client_key
            highlighted = row == self._highlighted_index
            button = ctk.CTkButton(
                results,
                text=self._display_by_key[key],
                anchor="w",
                height=self._ROW_HEIGHT - 2,
                corner_radius=6,
                fg_color=(
                    COLORS["accent_selected"]
                    if highlighted
                    else COLORS["surface_alt"]
                    if active
                    else "transparent"
                ),
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["accent_text"] if highlighted else COLORS["ink"],
                command=lambda selected_key=key: self._confirm(selected_key),
            )
            button.grid(row=row, column=0, sticky="ew", padx=4, pady=1)
            button.bind("<Enter>", lambda _event, index=row: self._set_highlight(index))

    def _set_highlight(self, index: int) -> None:
        """Destaca um resultado sem confirmar a troca de cliente."""
        if index < 0 or index >= len(self._matches) or index == self._highlighted_index:
            return
        results = self._results
        if results is None:
            return
        buttons = results.winfo_children()
        previous = self._highlighted_index
        if previous is not None:
            previous_key = self._matches[previous][0]
            buttons[previous].configure(
                fg_color=COLORS["surface_alt"] if previous_key == self._active_client_key else "transparent",
                text_color=COLORS["ink"],
            )
        self._highlighted_index = index
        buttons[index].configure(
            fg_color=COLORS["accent_selected"],
            text_color=COLORS["accent_text"],
        )

    def _move_highlight(self, event: object) -> str:
        """Move o destaque com as setas e mantém o resultado visível."""
        if not self._matches:
            return "break"
        direction = -1 if getattr(event, "keysym", "") == "Up" else 1
        current = self._highlighted_index
        if current is None:
            current = 0 if direction > 0 else len(self._matches) - 1
        else:
            current = (current + direction) % len(self._matches)
        self._set_highlight(current)
        if isinstance(self._results, PickerResults):
            self._results.reveal(current)
        return "break"

    def _confirm_highlight(self, _event: object) -> str:
        """Confirma somente o item destacado, se houver resultados."""
        if self._highlighted_index is not None and self._matches:
            self._confirm(self._matches[self._highlighted_index][0])
        return "break"

    def _cancel(self, _event: object = None) -> str:
        """Fecha a pesquisa sem confirmar a opção destacada."""
        self.close()
        return "break"

    def _on_focus_out(self, _event: object) -> None:
        """Descarta a pesquisa quando o foco deixa o seletor flutuante."""
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
        """Fecha a lista sem alterar o cliente confirmado."""
        popup, self._popup = self._popup, None
        root = self._root()
        for sequence, binding_id in self._popup_bindings:
            # unbind_all apagaria também os handlers de scroll do CustomTkinter.
            root._unbind(("bind", "all", sequence), binding_id)
        self._popup_bindings.clear()
        self._search_var = None
        self._results = None
        self._search_entry = None
        self._matches = ()
        self._highlighted_index = None
        self._popup_above = False
        if popup is not None and popup.winfo_exists():
            popup.destroy()

    def _confirm(self, client_key: str) -> None:
        self.close()
        if self._enabled:
            self._on_selected(client_key)
            if self.winfo_exists():
                self.winfo_toplevel().focus_force()

    def _refresh_label(self) -> None:
        self._button.set(self._display_by_key[self._active_client_key])
