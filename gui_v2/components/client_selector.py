"""Seletor visual de cliente e parâmetros de execução."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import customtkinter as ctk

from gui_v2.components.client_picker import ClientPicker
from gui_v2.theme import COLORS

SPEED_LABELS = {0: "Rápido", 750: "Médio", 1500: "Lento"}


class ClientSelector(ctk.CTkFrame):
    """Apresenta configuração recebida do controlador sem persistir alterações."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        clients: Mapping[str, str],
        active_client_key: str,
        url: str,
        speed_ms: int,
        on_open_codegen: Callable[[], None],
        on_client_selected: Callable[[str], None],
        on_speed_changed: Callable[[int], None],
    ) -> None:
        super().__init__(
            master, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"],
        )
        self._on_open_codegen = on_open_codegen
        self._on_client_selected = on_client_selected
        self._on_speed_changed = on_speed_changed
        self._client_names = dict(clients)
        for column in range(4):
            self.grid_columnconfigure(column, weight=1 if column in (0, 1, 2) else 0)
        self._build(active_client_key, url, speed_ms)

    @property
    def url(self) -> str:
        """Devolve a URL exibida para a ação do Codegen."""
        return self._url_entry.get().strip()

    def set_client(self, client_key: str, url: str) -> None:
        """Atualiza cliente e URL apresentados pelo seletor."""
        self._client_picker.set_active_client(client_key)
        self._set_url(url)

    def set_enabled(self, enabled: bool) -> None:
        """Bloqueia o seletor de cliente durante uma execução."""
        self._client_picker.set_enabled(enabled)

    def _build(self, active_client_key: str, url: str, speed_ms: int) -> None:
        client_box = self._field_container("Cliente", 0)
        self._client_picker = ClientPicker(
            client_box,
            clients=self._client_names,
            active_client_key=active_client_key,
            on_selected=self._on_client_selected,
        )
        self._client_picker.grid(row=1, column=0, sticky="ew")
        self._url_entry = self._field("URL", url, 1)
        self._url_entry.configure(state="readonly")
        speed_box = self._field_container("Velocidade", 2)
        self._speed_picker = ClientPicker(
            speed_box,
            clients={str(value): label for value, label in SPEED_LABELS.items()},
            active_client_key=str(speed_ms),
            on_selected=self._speed_changed,
            searchable=False,
        )
        self._speed_picker.grid(row=1, column=0, sticky="ew")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=3, padx=(8, 20), pady=(43, 14))
        ctk.CTkButton(
            actions, text="Codegen", width=92, height=36, corner_radius=9,
            fg_color=COLORS["accent_fill"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_open_codegen,
        ).pack(side="left", padx=(0, 8))

    def _speed_changed(self, value: str) -> None:
        """Encaminha a velocidade escolhida como atraso em milissegundos."""
        self._speed_picker.set_active_client(value)
        self._on_speed_changed(int(value))

    def _set_url(self, value: str) -> None:
        self._url_entry.configure(state="normal")
        self._url_entry.delete(0, "end")
        self._url_entry.insert(0, value)
        self._url_entry.configure(state="readonly")

    def _field(self, label: str, value: str, column: int) -> ctk.CTkBaseClass:
        box = self._field_container(label, column)
        widget = ctk.CTkEntry(box, height=36, corner_radius=8, border_color=COLORS["border"])
        widget.insert(0, value)
        widget.grid(row=1, column=0, sticky="ew")
        return widget

    def _field_container(self, label: str, column: int) -> ctk.CTkFrame:
        """Cria a coluna rotulada usada por campos e pelo seletor compartilhado."""
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.grid(row=0, column=column, sticky="ew", padx=(20, 8), pady=(16, 14))
        box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            box,
            text=label,
            anchor="w",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 5))
        return box
