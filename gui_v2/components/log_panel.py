"""Painel de logs da nova interface."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from gui_v2.theme import COLORS


class LogPanel(ctk.CTkFrame):
    """Apresenta a saída da execução demonstrativa sem conhecer sua engine."""

    MAX_LINES = 10_000

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_toggle_expanded: Callable[[], None],
        on_toggle_complete: Callable[[], None],
        on_clear: Callable[[], None],
    ) -> None:
        super().__init__(
            master, height=156, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"],
        )
        self._on_toggle_expanded = on_toggle_expanded
        self._on_toggle_complete = on_toggle_complete
        self._on_clear = on_clear
        self._follow_tail = True
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def append(self, text: str) -> None:
        """Inclui um bloco no fim do painel, descarta o excesso antigo e mantém o fim visível."""
        if not text or not self.winfo_exists() or not self._text_box.winfo_exists():
            return
        self._text_box.configure(state="normal")
        self._text_box.insert("end", text)
        line_count = int(self._text_box.index("end-1c").split(".")[0])
        if line_count > self.MAX_LINES:
            self._text_box.delete("1.0", f"{line_count - self.MAX_LINES + 1}.0")
        if self._follow_tail:
            self._text_box.see("end")
        self._text_box.configure(state="disabled")

    def clear(self) -> None:
        """Limpa somente o conteúdo apresentado na interface."""
        if not self.winfo_exists() or not self._text_box.winfo_exists():
            return
        self._text_box.configure(state="normal")
        self._text_box.delete("1.0", "end")
        self._text_box.configure(state="disabled")
        self._follow_tail = True

    def _copy_logs(self) -> None:
        """Copia o texto atualmente visível no painel."""
        content = self._text_box.get("1.0", "end-1c")
        if not content:
            return
        self.clipboard_clear()
        self.clipboard_append(content)

    def _request_clear(self) -> None:
        """Pede ao controlador para esquecer o histórico e limpa a caixa visível."""
        self._on_clear()
        self.clear()

    def set_expanded(self, expanded: bool) -> None:
        """Ajusta a apresentação interna conforme o modo do painel."""
        self.configure(
            height=max(320, int(self.winfo_toplevel().winfo_height() * 0.6)) if expanded else 156
        )
        self.grid_propagate(not expanded)
        self.grid_rowconfigure(1, weight=1 if expanded else 0)
        self._text_box.grid_configure(sticky="nsew" if expanded else "ew")
        self._expand_button.configure(text="Restaurar" if expanded else "Expandir")

    def resize_expanded(self) -> None:
        """Atualiza a altura ampliada após redimensionar a janela."""
        if not self.grid_propagate():
            self.configure(height=max(320, int(self.winfo_toplevel().winfo_height() * 0.6)))

    def set_complete_mode(self, complete: bool) -> None:
        """Atualiza o rótulo do modo de saída ativo."""
        self._mode_button.configure(text="Simplificado" if complete else "Completo")

    def set_font_size(self, size: int) -> None:
        """Altera somente a fonte do conteúdo dos logs."""
        self._text_box.configure(font=("Consolas", size))

    def _build(self) -> None:
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(head, text="Painel de logs", text_color=COLORS["ink"],
                     font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w")
        self._mode_button = ctk.CTkButton(
            head, text="Completo", width=82, height=28, fg_color="transparent",
            hover_color=COLORS["surface_alt"], text_color=COLORS["muted"],
            command=self._on_toggle_complete,
        )
        self._mode_button.grid(row=0, column=1, padx=(0, 6))
        self._expand_button = ctk.CTkButton(
            head, text="Expandir", width=74, height=28, fg_color="transparent",
            hover_color=COLORS["surface_alt"], text_color=COLORS["muted"],
            command=self._on_toggle_expanded,
        )
        self._expand_button.grid(row=0, column=2, padx=(0, 6))
        ctk.CTkButton(head, text="⌫", width=32, height=28, fg_color="transparent",
                      hover_color=COLORS["surface_alt"], text_color=COLORS["muted"],
                      command=self._request_clear).grid(row=0, column=3)
        ctk.CTkButton(head, text="Copiar", width=64, height=28, fg_color="transparent",
                      hover_color=COLORS["surface_alt"], text_color=COLORS["muted"],
                      command=self._copy_logs).grid(row=0, column=4, padx=(6, 0))
        self._text_box = ctk.CTkTextbox(
            self, height=92, corner_radius=8, fg_color=COLORS["surface_alt"],
            font=("Consolas", 11), border_width=0,
        )
        self._text_box.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))
        for sequence in ("<MouseWheel>", "<ButtonRelease-1>", "<KeyRelease>"):
            self._text_box.bind(sequence, self._schedule_follow_tail_update, add=True)
        self.append("Interface pronta. Selecione um teste para executar com Pytest.\n")

    def _schedule_follow_tail_update(self, _event: object) -> None:
        self.after_idle(self._update_follow_tail)

    def _update_follow_tail(self) -> None:
        """Mantém autoscroll apenas quando a leitura já está no fim."""
        if self.winfo_exists():
            _start, end = self._text_box.yview()
            self._follow_tail = end >= 0.999
