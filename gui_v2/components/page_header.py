"""Cabeçalho compartilhado das páginas da nova interface."""

from __future__ import annotations

import customtkinter as ctk

from gui_v2.theme import COLORS


class PageHeader(ctk.CTkFrame):
    """Exibe título, subtítulo e seletor de aparência de uma página."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        title: str,
        subtitle: str,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self, text=title, anchor="w", text_color=COLORS["ink"],
            font=ctk.CTkFont(size=27, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            self, text=subtitle, anchor="w", text_color=COLORS["muted"],
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
