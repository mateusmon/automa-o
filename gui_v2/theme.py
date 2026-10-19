"""Constantes visuais compartilhadas pela nova interface ASI Automação."""

from __future__ import annotations


DEFAULT_ACCENT_ID = "vermelho_suave"
ACCENT_PRESETS = {
    "vermelho_suave": {
        "label": "Vermelho suave",
        "fill": ("#B83B44", "#C44D55"),
        "hover": ("#A32F39", "#C74E56"),
        "text": ("#B83B44", "#EE9299"),
        "selected": ("#FBEAED", "#1C2028"),
    },
    "azul": {
        "label": "Azul",
        "fill": ("#355FAD", "#5274BE"),
        "hover": ("#2A529B", "#5475BC"),
        "text": ("#355FAD", "#93B5F1"),
        "selected": ("#EAF0FC", "#1C2028"),
    },
    "verde": {
        "label": "Verde",
        "fill": ("#176D67", "#308079"),
        "hover": ("#125D57", "#348078"),
        "text": ("#176D67", "#75CFC4"),
        "selected": ("#E7F4F1", "#1C2028"),
    },
    "violeta": {
        "label": "Violeta",
        "fill": ("#6654A8", "#7C64B9"),
        "hover": ("#594695", "#7F67BA"),
        "text": ("#6654A8", "#BBA8F2"),
        "selected": ("#F0ECFA", "#1C2028"),
    },
}


COLORS = {
    "accent_fill": ("#B83B44", "#C44D55"),
    "accent_hover": ("#A32F39", "#C74E56"),
    "accent_text": ("#B83B44", "#EE9299"),
    "accent_light": "#B83B44",
    "sentinel_fill": ("#D92929", "#D92929"),
    "sentinel_hover": ("#B91F1F", "#C44D55"),
    "sentinel_text": ("#B91F1F", "#F08080"),
    "accent_selected": ("#FBEAED", "#1C2028"),
    "sentinel_selected": ("#FDECEC", "#1C2028"),
    "error": ("#B42335", "#F4909C"),
    "error_fill": ("#B42335", "#C44D55"),
    "error_hover": ("#921C2A", "#C74E56"),
    "orange": "#F47A20",
    "purple": "#5B57C8",
    "teal": "#209889",
    "ink": ("#253047", "#F5F7FB"),
    "muted": ("#6D7482", "#AAB0BC"),
    "page": ("#F5F6F8", "#12151B"),
    "surface": ("#FFFFFF", "#1C2028"),
    "surface_alt": ("#F0F2F5", "#232831"),
    "border": ("#E3E6EA", "#333946"),
    "success": "#24986A",
}


def apply_accent(accent_id: str) -> bool:
    """Aplica à paleta compartilhada um dos presets previamente medidos."""
    preset = ACCENT_PRESETS.get(accent_id)
    if preset is None:
        return False
    COLORS["accent_fill"] = preset["fill"]
    COLORS["accent_hover"] = preset["hover"]
    COLORS["accent_text"] = preset["text"]
    COLORS["accent_light"] = preset["fill"][0]
    COLORS["accent_selected"] = preset["selected"]
    # Sentinela também acompanha o preset escolhido; mantém tokens próprios para
    # permitir evolução visual separada sem prender a interface ao vermelho.
    COLORS["sentinel_fill"] = preset["fill"]
    COLORS["sentinel_hover"] = preset["hover"]
    COLORS["sentinel_text"] = preset["text"]
    COLORS["sentinel_selected"] = preset["selected"]
    return True


apply_accent(DEFAULT_ACCENT_ID)
