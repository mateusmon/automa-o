"""Carregamento e criação dos ícones da nova interface ASI Automação."""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw

from gui_v2.theme import COLORS


def load_module_image(icons_dir: Path, filename: str) -> ctk.CTkImage | None:
    """Carrega um ícone de módulo e aplica suas variantes claro e escuro."""
    path = icons_dir / filename
    if not path.exists():
        return None
    source = Image.open(path).convert("RGBA")
    alpha = source.getchannel("A")
    light_icon = Image.new("RGBA", source.size, "#253047")
    light_icon.putalpha(alpha)
    dark_icon = Image.new("RGBA", source.size, "#F5F7FB")
    dark_icon.putalpha(alpha)
    return ctk.CTkImage(light_image=light_icon, dark_image=dark_icon, size=(25, 25))


def create_target_icon() -> ctk.CTkImage:
    """Cria um alvo vetorial simples para o módulo Testes Específicos."""
    def draw(color: str) -> Image.Image:
        canvas = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        pen = ImageDraw.Draw(canvas)
        pen.ellipse((24, 24, 116, 116), outline=color, width=12)
        pen.ellipse((50, 50, 90, 90), outline=color, width=12)
        pen.line((70, 5, 70, 35), fill=color, width=12)
        pen.line((70, 105, 70, 135), fill=color, width=12)
        pen.line((5, 70, 35, 70), fill=color, width=12)
        pen.line((105, 70, 135, 70), fill=color, width=12)
        return canvas.resize((35, 35), Image.Resampling.LANCZOS)

    return ctk.CTkImage(light_image=draw("#253047"), dark_image=draw("#F5F7FB"), size=(25, 25))


def create_nav_icon(
    kind: str,
    active: bool,
    active_colors: tuple[str, str] | None = None,
) -> ctk.CTkImage:
    """Cria ícones do menu sem depender dos glifos instalados no Windows."""
    def draw(color: str) -> Image.Image:
        canvas = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        pen = ImageDraw.Draw(canvas)
        if kind == "play":
            pen.ellipse((13, 13, 107, 107), outline=color, width=10)
            pen.polygon((48, 35, 48, 85, 86, 60), fill=color)
        elif kind == "shield":
            pen.line((60, 8, 103, 25, 96, 76, 60, 110, 24, 76, 17, 25, 60, 8),
                     fill=color, width=10, joint="curve")
            pen.ellipse((48, 45, 72, 69), fill=color)
            pen.line((60, 67, 60, 88), fill=color, width=9)
        elif kind == "spark":
            pen.polygon((60, 7, 72, 45, 110, 60, 72, 75, 60, 113, 48, 75, 10, 60, 48, 45),
                        outline=color, fill=None)
            pen.line((60, 7, 72, 45, 110, 60, 72, 75, 60, 113, 48, 75, 10, 60, 48, 45, 60, 7),
                     fill=color, width=9, joint="curve")
        elif kind == "panel":
            pen.rounded_rectangle((15, 17, 105, 103), radius=8, outline=color, width=9)
            pen.line((60, 18, 60, 102), fill=color, width=8)
        else:
            pen.ellipse((25, 25, 95, 95), outline=color, width=14)
            pen.ellipse((48, 48, 72, 72), fill=color)
            for box in ((52, 4, 68, 31), (52, 89, 68, 116), (4, 52, 31, 68), (89, 52, 116, 68),
                        (17, 17, 37, 37), (83, 17, 103, 37), (17, 83, 37, 103), (83, 83, 103, 103)):
                pen.rounded_rectangle(box, radius=5, fill=color)
        return canvas.resize((30, 30), Image.Resampling.LANCZOS)

    active_colors = active_colors or COLORS["accent_text"]
    light = active_colors[0] if active else "#6D7482"
    dark = active_colors[1] if active else "#AAB0BC"
    return ctk.CTkImage(light_image=draw(light), dark_image=draw(dark), size=(18, 18))


def create_more_icon() -> ctk.CTkImage:
    """Cria o ícone do seletor de módulos adicionais."""
    def draw(color: str) -> Image.Image:
        canvas = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        pen = ImageDraw.Draw(canvas)
        for y in (18, 58):
            for x in (18, 58):
                pen.rounded_rectangle((x, y, x + 24, y + 24), radius=5, outline=color, width=7)
        return canvas.resize((30, 30), Image.Resampling.LANCZOS)

    return ctk.CTkImage(light_image=draw("#253047"), dark_image=draw("#F5F7FB"), size=(23, 23))
