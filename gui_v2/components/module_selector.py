"""Seletor visual de módulos da execução demonstrativa."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

import customtkinter as ctk

from gui_v2.assets import create_more_icon
from gui_v2.theme import COLORS


class ModuleSelector(ctk.CTkFrame):
    """Exibe módulos principais e o seletor sobreposto de módulos adicionais."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        picker_parent: ctk.CTkBaseClass,
        primary_modules: Sequence[str],
        module_colors: Mapping[str, str],
        current_module: str,
        available_modules: Callable[[], list[str]],
        image_loader: Callable[[str], ctk.CTkImage | None],
        on_module_selected: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._picker_parent = picker_parent
        self._primary_modules = tuple(primary_modules)
        self._module_colors = module_colors
        self._available_modules = available_modules
        self._image_loader = image_loader
        self._on_module_selected = on_module_selected
        self._current_module = current_module
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._picker: ctk.CTkFrame | None = None
        self._build()
        self.set_active(current_module)

    def set_active(self, module: str) -> None:
        """Atualiza a aparência do módulo selecionado."""
        self._current_module = module
        for name, button in self._buttons.items():
            active = name == module or (name == "Outros módulos" and module not in self._primary_modules)
            accent = self._module_colors.get(module, COLORS["accent_light"]) if name == "Outros módulos" and active else (
                self._module_colors[name] if name in self._module_colors else COLORS["accent_light"]
            )
            button.configure(
                border_color=accent if active else COLORS["border"],
                border_width=2 if active else 1,
                text_color=accent if active else COLORS["ink"],
            )

    def set_modules(self, colors: Mapping[str, str], active: str) -> None:
        """Atualiza a disponibilidade e a seleção após mudar de cliente."""
        self._module_colors = colors
        if self._picker is not None and self._picker.winfo_exists():
            self._picker.destroy()
            self._picker = None
        for name in self._primary_modules:
            self._buttons[name].configure(state="normal" if name in colors else "disabled")
        self.set_active(active)

    def _build(self) -> None:
        for column, module in enumerate((*self._primary_modules, "Outros módulos")):
            self.grid_columnconfigure(column, weight=1)
            if module == "Outros módulos":
                button = ctk.CTkButton(
                    self, text="Outros módulos  ▾", image=create_more_icon(), compound="left",
                    height=62, corner_radius=12, border_width=1, border_color=COLORS["border"],
                    fg_color=COLORS["surface"], hover_color=COLORS["surface_alt"],
                    text_color=COLORS["ink"], font=ctk.CTkFont(size=12, weight="bold"),
                    command=self._toggle_picker,
                )
                padx = (5, 5)
            else:
                button = ctk.CTkButton(
                    self, text=module, image=self._image_loader(module), compound="left",
                    height=62, corner_radius=12, border_width=1, border_color=COLORS["border"],
                    fg_color=COLORS["surface"], hover_color=COLORS["surface_alt"],
                    text_color=COLORS["ink"], font=ctk.CTkFont(size=12, weight="bold"),
                    command=lambda name=module: self._on_module_selected(name),
                )
                padx = (0 if column == 0 else 5, 5)
            button.grid(row=0, column=column, sticky="ew", padx=padx)
            self._buttons[module] = button

    def _toggle_picker(self) -> None:
        if self._picker is not None and self._picker.winfo_exists():
            self._picker.destroy()
            self._picker = None
            return

        picker = ctk.CTkFrame(
            self._picker_parent, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"],
        )
        self._picker = picker
        picker.place(
            in_=self._buttons["Outros módulos"], relx=1.0, rely=1.0,
            relwidth=1.0, y=8, anchor="ne",
        )
        picker.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(picker, text="Outros módulos", anchor="w", text_color=COLORS["ink"],
                     font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        available = self._available_modules()
        for row, module in enumerate(available, start=1):
            ctk.CTkButton(
                picker, text=module, image=self._image_loader(module), compound="left",
                anchor="w", height=44, corner_radius=10, fg_color=COLORS["surface_alt"],
                hover_color=COLORS["border"], text_color=COLORS["ink"],
                border_width=1, border_color=COLORS["border"],
                command=lambda name=module: self._choose_other_module(name),
            ).grid(row=row, column=0, sticky="ew", padx=10, pady=(0, 10))
        if not available:
            ctk.CTkLabel(picker, text="Nenhum outro módulo disponível", text_color=COLORS["muted"]).grid(
                row=1, column=0, padx=18, pady=18)
        picker.lift()

    def _choose_other_module(self, module: str) -> None:
        if self._picker is not None:
            self._picker.destroy()
            self._picker = None
        self._on_module_selected(module)
