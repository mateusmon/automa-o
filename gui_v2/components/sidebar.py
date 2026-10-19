"""Barra lateral de navegação da nova interface."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from gui_v2.assets import create_nav_icon
from gui_v2.theme import COLORS


class Sidebar(ctk.CTkFrame):
    """Exibe a marca e a navegação principal."""

    EXPANDED_WIDTH = 236
    COLLAPSED_WIDTH = 72
    PAGES = ("Execução", "Sentinela", "Configurações")
    _ICON_KINDS = {
        "Execução": "play",
        "Sentinela": "shield",
        "Configurações": "gear",
    }

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_page_selected: Callable[[str], None],
        on_collapsed_changed: Callable[[bool], None] | None = None,
        apply_layout_change: Callable[[Callable[[], None]], None] | None = None,
    ) -> None:
        super().__init__(master, width=self.EXPANDED_WIDTH, corner_radius=0, fg_color=COLORS["surface"])
        self._on_page_selected = on_page_selected
        self._on_collapsed_changed = on_collapsed_changed
        self._apply_layout_change = apply_layout_change or (lambda change: change())
        self.buttons: dict[str, ctk.CTkButton] = {}
        self._error_indicator_visible = False
        self._error_indicator: ctk.CTkLabel | None = None
        self._brand_mark: ctk.CTkLabel | None = None
        self._brand: ctk.CTkFrame | None = None
        self._brand_name: ctk.CTkLabel | None = None
        self._brand_subtitle: ctk.CTkLabel | None = None
        self._toggle_button: ctk.CTkButton | None = None
        self._collapsed = False
        self._active_page: str | None = None
        self._icons = self._build_icons()
        self._toggle_icon = create_nav_icon("panel", active=False)

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=20)
        self._build()

    @property
    def collapsed(self) -> bool:
        """Indica se a sidebar está no modo compacto."""
        return self._collapsed

    def toggle_collapsed(self) -> None:
        """Alterna a largura e os rótulos sem recriar a navegação ou as páginas."""
        collapsed = not self._collapsed
        self._apply_layout_change(lambda: self.set_collapsed(collapsed))
        if self._on_collapsed_changed is not None:
            self._on_collapsed_changed(collapsed)

    def set_collapsed(self, collapsed: bool) -> None:
        """Aplica imediatamente o modo expandido ou compacto."""
        if type(collapsed) is not bool:
            raise TypeError("O estado compacto da sidebar deve ser booleano.")
        if self._collapsed == collapsed:
            return

        self._collapsed = collapsed
        self.configure(width=self.COLLAPSED_WIDTH if collapsed else self.EXPANDED_WIDTH)
        if self._brand is not None:
            self._brand.grid_configure(padx=(12, 12) if collapsed else (22, 8))
            self._brand.grid_columnconfigure(0, weight=1 if collapsed else 0)
            self._brand.grid_columnconfigure(1, weight=0 if collapsed else 1)
        if self._brand_mark is not None:
            self._brand_mark.configure(
                width=44 if collapsed else 48,
                height=44 if collapsed else 48,
                font=ctk.CTkFont(size=14 if collapsed else 18, weight="bold"),
            )
            self._brand_mark.grid_configure(
                columnspan=2 if collapsed else 1,
                padx=0 if collapsed else (0, 12),
            )
        for label in (self._brand_name, self._brand_subtitle):
            if label is None:
                continue
            if collapsed:
                label.grid_remove()
            else:
                label.grid()
        for name, button in self.buttons.items():
            button.configure(
                text="" if collapsed else f"   {name}",
                anchor="center" if collapsed else "w",
                border_spacing=8 if collapsed else 10,
            )
            button.grid_configure(columnspan=2 if collapsed else 1, padx=4 if collapsed else 14)
        if self._error_indicator is not None:
            self._error_indicator.grid_configure(padx=(0, 4 if collapsed else 14))
            if not self._error_indicator_visible:
                self._error_indicator.grid_remove()
        if self._toggle_button is not None:
            self._toggle_button.configure(
                anchor="center" if collapsed else "w",
                border_spacing=8 if collapsed else 10,
            )
            self._toggle_button.grid_configure(columnspan=2 if collapsed else 1, padx=4 if collapsed else 14)

    def _build_icons(self) -> dict[str, dict[str, ctk.CTkImage]]:
        """Cria ícones ativos com a paleta corrente e mantém os ícones neutros."""
        return {
            name: {
                "normal": create_nav_icon(kind, active=False),
                "active": create_nav_icon(
                    kind,
                    active=True,
                    active_colors=COLORS["accent_text"],
                ),
            }
            for name, kind in self._ICON_KINDS.items()
        }

    def refresh_accent(self) -> None:
        """Atualiza os ícones e o item ativo após a troca do preset."""
        self._icons = self._build_icons()
        if self._active_page is not None:
            self.set_active(self._active_page)

    def set_active(self, page_name: str) -> None:
        """Atualiza somente a aparência do item de navegação ativo."""
        self._active_page = page_name
        for page, button in self.buttons.items():
            active = page == page_name
            active_color = COLORS["accent_text"]
            selected_color = COLORS["accent_selected"]
            button.configure(
                fg_color=selected_color if active else "transparent",
                text_color=active_color if active else COLORS["muted"],
                border_width=1 if active else 0,
                border_color=active_color,
                image=self._icons[page]["active" if active else "normal"],
            )
        if self._brand_mark is not None:
            self._brand_mark.configure(
                fg_color=(
                    COLORS["sentinel_fill"]
                    if page_name == "Sentinela"
                    else COLORS["accent_fill"]
                )
            )

    def _build(self) -> None:
        brand = ctk.CTkFrame(self, fg_color="transparent", height=64)
        brand.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(22, 8), pady=(14, 4))
        brand.grid_propagate(False)
        self._brand = brand
        brand.grid_columnconfigure(1, weight=1)
        self._brand_mark = ctk.CTkLabel(
            brand, text="ASI", width=48, height=48, corner_radius=12,
            fg_color=COLORS["accent_fill"], text_color="white",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self._brand_mark.grid(row=0, column=0, rowspan=2, padx=(0, 12))
        self._brand_name = ctk.CTkLabel(
            brand, text="ASI Automação", anchor="w", text_color=COLORS["ink"],
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        self._brand_name.grid(row=0, column=1, sticky="sw")
        self._brand_subtitle = ctk.CTkLabel(
            brand, text="Testes automatizados", anchor="w", text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
        )
        self._brand_subtitle.grid(row=1, column=1, sticky="nw")
        self._toggle_button = ctk.CTkButton(
            self,
            text="",
            image=self._toggle_icon,
            compound="left",
            anchor="w",
            width=38,
            height=46,
            corner_radius=10,
            border_spacing=10,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            command=self.toggle_collapsed,
        )
        self._toggle_button.grid(row=1, column=0, sticky="ew", padx=14, pady=(3, 13))

        for row, name in enumerate(self.PAGES, start=2):
            button = ctk.CTkButton(
                self, text=f"   {name}", image=self._icons[name]["normal"],
                compound="left", anchor="w", height=46,
                corner_radius=10, border_spacing=10, fg_color="transparent",
                hover_color=COLORS["surface_alt"], text_color=COLORS["muted"],
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda page=name: self._on_page_selected(page),
            )
            button.grid(row=row, column=0, sticky="ew", padx=14, pady=3)
            self.buttons[name] = button
            if name == "Configurações":
                self._error_indicator = ctk.CTkLabel(
                    self,
                    text="●",
                    width=12,
                    text_color=COLORS["error"],
                    font=ctk.CTkFont(size=12, weight="bold"),
                )
                self._error_indicator.grid(row=row, column=1, padx=(0, 14))
                self._error_indicator.grid_remove()

    def set_error_indicator(self, visible: bool) -> None:
        """Exibe ou oculta o ponto de erros ainda não consultados."""
        if self._error_indicator is None:
            return
        if (
            self._error_indicator_visible == visible
            and bool(self._error_indicator.grid_info()) == visible
        ):
            return
        self._error_indicator_visible = visible
        if visible:
            self._error_indicator.grid()
        else:
            self._error_indicator.grid_remove()
