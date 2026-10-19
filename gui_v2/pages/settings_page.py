"""Página de configurações pessoais da GUI."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from tkinter import StringVar, messagebox

import customtkinter as ctk

from gui_v2.components.page_header import PageHeader
from gui_v2.services.gui_error_service import GuiErrorLogSnapshot
from gui_v2.services.preferences_service import LOG_FONT_SIZES
from gui_v2.theme import ACCENT_PRESETS, COLORS


class SettingsPage(ctk.CTkFrame):
    """Apresenta e atualiza preferências locais da interface e da Sentinela."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_theme_changed: Callable[[str], None],
        current_theme: str,
        log_level: str,
        log_levels: Sequence[str],
        log_font_size: int,
        full_output: bool,
        browser_visible: bool,
        sentinel_ttl_days: int,
        on_log_level_changed: Callable[[str], None],
        on_log_font_size_changed: Callable[[int], None],
        on_full_output_changed: Callable[[bool], None],
        on_browser_visible_changed: Callable[[bool], None],
        on_sentinel_ttl_changed: Callable[[int], None],
        accent_id: str,
        on_accent_changed: Callable[[str, str], None],
        gui_error_snapshot: GuiErrorLogSnapshot,
        on_refresh_gui_errors: Callable[[], GuiErrorLogSnapshot],
        on_gui_errors_viewed: Callable[[GuiErrorLogSnapshot], None],
        on_clear_gui_errors: Callable[[], str | None],
        initial_tab: str = "Geral",
    ) -> None:
        super().__init__(master, fg_color=COLORS["page"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        PageHeader(
            self,
            "Configurações",
            "Preferências, execução e diagnóstico da interface",
        ).grid(row=0, column=0, sticky="ew", padx=32, pady=(26, 16))

        self._on_refresh_gui_errors = on_refresh_gui_errors
        self._on_gui_errors_viewed = on_gui_errors_viewed
        self._on_clear_gui_errors = on_clear_gui_errors
        self._log_font_size = log_font_size
        self._tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["surface"],
            segmented_button_fg_color=COLORS["surface_alt"],
            segmented_button_selected_color=COLORS["accent_fill"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["accent_hover"],
            segmented_button_unselected_hover_color=COLORS["accent_fill"],
            segmented_button_font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF",
            command=self._on_settings_tab_changed,
        )
        self._tabs.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 28))
        general_tab = self._tabs.add("Geral")
        themes_tab = self._tabs.add("Temas")
        errors_tab = self._tabs.add("Erros da GUI")
        # O CTkTabview não expõe dimensões individuais para seus seletores.
        self._tabs._segmented_button.configure(width=390, height=36, dynamic_resizing=False)
        for tab_button in self._tabs._segmented_button._buttons_dict.values():
            tab_button.configure(width=130, height=36)
        general_tab.grid_rowconfigure(0, weight=1)
        general_tab.grid_columnconfigure(0, weight=1)
        themes_tab.grid_columnconfigure(0, weight=1)
        errors_tab.grid_rowconfigure(0, weight=1)
        errors_tab.grid_columnconfigure(0, weight=1)
        self._tabs.set(
            initial_tab
            if initial_tab in {"Geral", "Temas", "Erros da GUI"}
            else "Geral"
        )
        self._gui_error_content = ""
        self._appearance_switch = self._add_appearance_option(
            themes_tab, current_theme, on_theme_changed
        )
        self._build_gui_errors_tab(errors_tab, gui_error_snapshot)

        card = ctk.CTkFrame(
            general_tab,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        card.grid_columnconfigure(0, weight=1)
        self._log_level_combo = self._add_log_level_option(
            card, log_level, log_levels, on_log_level_changed
        )
        self._add_switch_option(
            card,
            row=1,
            title="Saída completa",
            description="Mostra a saída integral do Pytest e stacktraces",
            value=full_output,
            on_changed=on_full_output_changed,
        )
        self._add_switch_option(
            card,
            row=2,
            title="Navegador visível",
            description="Permite acompanhar as ações automatizadas",
            value=browser_visible,
            on_changed=on_browser_visible_changed,
        )
        self._add_sentinel_ttl_option(
            card, row=3, value=sentinel_ttl_days, on_changed=on_sentinel_ttl_changed
        )
        self._log_font_size_combo = self._add_log_font_size_option(
            card, row=4, value=log_font_size, on_changed=on_log_font_size_changed
        )
        ctk.CTkLabel(
            card,
            text="Preferências salvas localmente.",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
        ).grid(row=5, column=0, sticky="w", padx=24, pady=28)
        self._add_accent_options(
            themes_tab,
            self._tabs,
            accent_id,
            on_accent_changed,
        )

    def _build_gui_errors_tab(
        self,
        tab: ctk.CTkFrame,
        snapshot: GuiErrorLogSnapshot,
    ) -> None:
        """Apresenta o histórico interno sem misturá-lo à saída das execuções."""
        card = ctk.CTkFrame(
            tab,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkFrame(card, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 8))
        heading.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            heading,
            text="Erros internos da GUI",
            anchor="w",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            heading,
            text=(
                "Diagnósticos locais; a saída do Pytest e da Sentinela "
                "fica nas respectivas páginas."
            ),
            anchor="w",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._copy_errors_button = ctk.CTkButton(
            heading,
            text="Copiar tudo",
            width=104,
            height=32,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["ink"],
            command=self._copy_gui_errors,
        )
        self._copy_errors_button.grid(row=0, column=1, rowspan=2, padx=(8, 0))
        ctk.CTkButton(
            heading,
            text="Atualizar",
            width=92,
            height=32,
            fg_color=COLORS["accent_fill"],
            hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            command=lambda: self.refresh_gui_errors(mark_viewed=True),
        ).grid(row=0, column=2, rowspan=2, padx=(8, 0))
        self._clear_errors_button = ctk.CTkButton(
            heading,
            text="Limpar histórico",
            width=128,
            height=32,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["ink"],
            command=self._clear_gui_errors,
        )
        self._clear_errors_button.grid(row=0, column=3, rowspan=2, padx=(8, 0))

        self._gui_error_status = ctk.CTkLabel(
            card,
            text="",
            anchor="w",
            justify="left",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
        )
        self._gui_error_status.grid(
            row=1, column=0, sticky="ew", padx=22, pady=(0, 8)
        )
        self._gui_error_textbox = ctk.CTkTextbox(
            card,
            height=420,
            corner_radius=8,
            fg_color=COLORS["surface_alt"],
            text_color=COLORS["ink"],
            font=("Consolas", self._log_font_size),
            wrap="word",
            activate_scrollbars=True,
        )
        self._gui_error_textbox.grid(
            row=2, column=0, sticky="nsew", padx=22, pady=(0, 18)
        )
        self._render_gui_error_snapshot(snapshot)

    @property
    def current_tab(self) -> str:
        """Nome da aba selecionada atualmente."""
        return self._tabs.get()

    def _on_settings_tab_changed(self) -> None:
        """Marca como visto somente quando a aba de erros é selecionada."""
        if self.current_tab == "Erros da GUI":
            self.refresh_gui_errors(mark_viewed=True)

    def refresh_gui_errors(self, *, mark_viewed: bool = False) -> None:
        """Atualiza o histórico e opcionalmente registra a consulta atual."""
        snapshot = self._on_refresh_gui_errors()
        self._render_gui_error_snapshot(snapshot)
        if mark_viewed and snapshot.available:
            self._on_gui_errors_viewed(snapshot)

    def _render_gui_error_snapshot(self, snapshot: GuiErrorLogSnapshot) -> None:
        """Renderiza conteúdo, estado vazio ou falha de leitura."""
        self._gui_error_content = snapshot.content if snapshot.available else ""
        if not snapshot.available:
            status = f"Não foi possível consultar o histórico: {snapshot.error_message}"
            status_color = COLORS["error"]
        elif snapshot.content:
            status = "Histórico de erros internos da GUI v2."
            status_color = COLORS["muted"]
        else:
            status = "Nenhum erro interno registrado até agora."
            status_color = COLORS["muted"]
        self._gui_error_status.configure(text=status, text_color=status_color)

        self._gui_error_textbox.configure(state="normal")
        self._gui_error_textbox.delete("1.0", "end")
        if snapshot.available and snapshot.content:
            self._gui_error_textbox.insert("1.0", snapshot.content)
        self._gui_error_textbox.configure(state="disabled")
        self._copy_errors_button.configure(
            state="normal" if self._gui_error_content else "disabled"
        )
        self._clear_errors_button.configure(
            state="normal" if self._gui_error_content else "disabled"
        )

    def _clear_gui_errors(self) -> None:
        """Confirma a exclusão do histórico e atualiza a tela."""
        if not self._gui_error_content:
            return
        if not messagebox.askyesno(
            "Limpar histórico de erros",
            "Apagar todos os erros internos registrados da GUI, incluindo as cópias antigas?",
            parent=self,
        ):
            return
        error = self._on_clear_gui_errors()
        if error is not None:
            messagebox.showerror("Erro ao limpar histórico", error, parent=self)
        self.refresh_gui_errors()

    def _copy_gui_errors(self) -> None:
        """Copia o histórico atualmente carregado para a área de transferência."""
        if not self._gui_error_content:
            return
        self.clipboard_clear()
        self.clipboard_append(self._gui_error_content)

    @staticmethod
    def _add_appearance_option(
        tab: ctk.CTkFrame,
        current_theme: str,
        on_changed: Callable[[str], None],
    ) -> ctk.CTkSegmentedButton:
        card = ctk.CTkFrame(
            tab,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 12))
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card,
            text="Modo de aparência",
            anchor="w",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 8))
        appearance_switch = ctk.CTkSegmentedButton(
            card,
            values=["Sistema", "Claro", "Escuro"],
            command=lambda value: SettingsPage._change_appearance(
                appearance_switch, value, on_changed
            ),
            width=220,
            height=36,
            fg_color=COLORS["surface"],
            selected_color=COLORS["accent_fill"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["surface_alt"],
            text_color=COLORS["ink"],
        )
        appearance_switch.set(current_theme)
        appearance_switch.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 18))
        SettingsPage._style_appearance_text(appearance_switch, current_theme)
        return appearance_switch

    @staticmethod
    def _change_appearance(
        switch: ctk.CTkSegmentedButton,
        value: str,
        on_changed: Callable[[str], None],
    ) -> None:
        on_changed(value)
        SettingsPage._style_appearance_text(switch, value)

    @staticmethod
    def _style_appearance_text(
        switch: ctk.CTkSegmentedButton,
        selected_value: str,
    ) -> None:
        for value, button in switch._buttons_dict.items():
            button.configure(
                text_color="#FFFFFF" if value == selected_value else COLORS["ink"]
            )

    @staticmethod
    def _add_accent_options(
        tab: ctk.CTkFrame,
        tabs: ctk.CTkTabview,
        accent_id: str,
        on_changed: Callable[[str, str], None],
    ) -> None:
        card = ctk.CTkFrame(
            tab,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=1, column=0, sticky="new", padx=4, pady=4)
        card.grid_columnconfigure((0, 1), weight=1, uniform="accent_presets")
        ctk.CTkLabel(
            card,
            text="Cor predominante",
            anchor="w",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(22, 4))
        ctk.CTkLabel(
            card,
            text="A escolha atualiza as páginas comuns e o menu nesta sessão.",
            anchor="w",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=22, pady=(0, 16))

        for index, (preset_id, preset) in enumerate(ACCENT_PRESETS.items()):
            selected = preset_id == accent_id
            label = f"✓  {preset['label']}" if selected else preset["label"]
            ctk.CTkButton(
                card,
                text=label,
                height=50,
                corner_radius=10,
                fg_color=preset["fill"],
                hover_color=preset["hover"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=13, weight="bold"),
                border_width=2 if selected else 0,
                border_color="#FFFFFF",
                command=lambda selected_id=preset_id: on_changed(selected_id, tabs.get()),
            ).grid(
                row=2 + index // 2,
                column=index % 2,
                sticky="ew",
                padx=12,
                pady=(6, 10),
            )

    @staticmethod
    def _add_log_level_option(
        card: ctk.CTkFrame,
        log_level: str,
        log_levels: Sequence[str],
        on_changed: Callable[[str], None],
    ) -> ctk.CTkComboBox:
        item = SettingsPage._row(
            card,
            0,
            "Nível dos logs",
            "Define o menor nível exibido no painel",
        )
        option = ctk.CTkComboBox(
            item,
            values=list(log_levels),
            state="readonly",
            command=on_changed,
            width=180,
            height=36,
            corner_radius=8,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            button_color=COLORS["surface_alt"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=("#EEF1F5", "#303641"),
            dropdown_text_color=COLORS["ink"],
            text_color=COLORS["ink"],
        )
        option.set(log_level)
        option.grid(row=0, column=1, rowspan=2, sticky="e")
        return option

    @staticmethod
    def _add_log_font_size_option(
        card: ctk.CTkFrame,
        row: int,
        value: int,
        on_changed: Callable[[int], None],
    ) -> ctk.CTkComboBox:
        item = SettingsPage._row(
            card, row, "Tamanho da fonte dos logs", "Aplica-se aos logs de Execução, Sentinela e Erros da GUI."
        )
        option = ctk.CTkComboBox(
            item,
            values=[str(size) for size in LOG_FONT_SIZES],
            state="readonly",
            command=lambda selected: on_changed(int(selected)),
            width=92,
            height=36,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            button_color=COLORS["surface_alt"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=("#EEF1F5", "#303641"),
            dropdown_text_color=COLORS["ink"],
            text_color=COLORS["ink"],
        )
        option.set(str(value))
        option.grid(row=0, column=1, rowspan=2, sticky="e")
        return option

    def set_log_font_size(self, size: int) -> None:
        """Aplica a preferência ao histórico de erros que já está aberto."""
        self._log_font_size = size
        self._log_font_size_combo.set(str(size))
        self._gui_error_textbox.configure(font=("Consolas", size))

    @staticmethod
    def _add_switch_option(
        card: ctk.CTkFrame,
        row: int,
        title: str,
        description: str,
        value: bool,
        on_changed: Callable[[bool], None],
    ) -> None:
        item = SettingsPage._row(card, row, title, description)
        switch = ctk.CTkSwitch(
            item,
            text="",
            command=lambda: on_changed(bool(switch.get())),
            onvalue=True,
            offvalue=False,
            progress_color=COLORS["accent_fill"],
        )
        if value:
            switch.select()
        else:
            switch.deselect()
        switch.grid(row=0, column=1, rowspan=2, sticky="e")

    @staticmethod
    def _add_sentinel_ttl_option(
        card: ctk.CTkFrame,
        row: int,
        value: int,
        on_changed: Callable[[int], None],
    ) -> None:
        item = SettingsPage._row(
            card,
            row,
            "Retenção dos runs da Sentinela",
            "Dias antes da limpeza automática; informe um inteiro de 1 a 365.",
        )
        value_var = StringVar(master=item, value=str(value))
        entry = ctk.CTkEntry(
            item,
            textvariable=value_var,
            width=92,
            height=36,
            validate="key",
            validatecommand=(SettingsPage._validate_ttl_text, "%P"),
        )
        entry.grid(row=0, column=1, rowspan=2, sticky="e")
        info = ctk.CTkLabel(
            item,
            text="Alterações válidas são salvas automaticamente.",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=10),
        )
        info.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))

        def changed(*_args: str) -> None:
            raw_value = value_var.get()
            ttl_days = int(raw_value) if raw_value.isascii() and raw_value.isdigit() else None
            if ttl_days is not None and 1 <= ttl_days <= 365:
                entry.configure(border_color=COLORS["border"])
                info.configure(
                    text="Alterações válidas são salvas automaticamente.",
                    text_color=COLORS["muted"],
                )
                on_changed(ttl_days)
            else:
                entry.configure(border_color=COLORS["orange"])
                info.configure(
                    text="Informe um inteiro entre 1 e 365 dias.",
                    text_color=COLORS["orange"],
                )

        value_var.trace_add("write", changed)

    @staticmethod
    def _validate_ttl_text(value: str) -> bool:
        """Permite apagar o campo durante a edição e limita a três algarismos."""
        return (value.isascii() and value.isdigit() and len(value) <= 3) or value == ""

    @staticmethod
    def _row(card: ctk.CTkFrame, row: int, title: str, description: str) -> ctk.CTkFrame:
        item = ctk.CTkFrame(card, fg_color="transparent")
        item.grid(row=row, column=0, sticky="ew", padx=24, pady=(24 if row == 0 else 10, 8))
        item.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            item,
            text=title,
            anchor="w",
            text_color=COLORS["ink"],
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            item,
            text=description,
            anchor="w",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
        ctk.CTkFrame(card, height=1, fg_color=COLORS["border"]).grid(
            row=row, column=0, sticky="sew", padx=24
        )
        return item
