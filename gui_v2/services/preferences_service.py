"""Leitura e gravação local das preferências da nova GUI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import os
import tempfile
from typing import Any

from gui_v2.theme import ACCENT_PRESETS, DEFAULT_ACCENT_ID


PREFERENCES_PATH = Path(__file__).resolve().parents[1] / "preferences.local.json"
SCHEMA_VERSION = 3
SUPPORTED_SCHEMA_VERSIONS = {1, 2, SCHEMA_VERSION}
THEMES = {"Sistema", "Claro", "Escuro"}
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
SPEED_MS_VALUES = (0, 750, 1500)
LOG_FONT_SIZES = tuple(range(9, 21))


@dataclass(frozen=True, slots=True)
class GuiPreferences:
    """Preferências pessoais atualmente expostas pela GUI."""

    theme: str = "Sistema"
    speed_ms: int = 0
    log_level: str = "INFO"
    full_output: bool = False
    browser_visible: bool = True
    accent_id: str = DEFAULT_ACCENT_ID
    sentinel_ttl_days: int | None = None
    sidebar_collapsed: bool = False
    logs_expanded: bool = False
    sentinel_logs_expanded: bool = False
    log_font_size: int = 11


DEFAULT_PREFERENCES = GuiPreferences()


class PreferencesService:
    """Persiste preferências pessoais em arquivo local ignorado pelo SVN."""

    def __init__(self, path: Path = PREFERENCES_PATH) -> None:
        self._path = path

    def load(self) -> GuiPreferences:
        """Carrega preferências válidas e aplica padrões a campos inválidos."""
        try:
            with self._path.open(encoding="utf-8") as stream:
                data: Any = json.load(stream)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return DEFAULT_PREFERENCES

        if (
            not isinstance(data, dict)
            or type(data.get("schema_version")) is not int
            or data["schema_version"] not in SUPPORTED_SCHEMA_VERSIONS
        ):
            return DEFAULT_PREFERENCES

        theme = data.get("theme")
        speed_ms = data.get("speed_ms", DEFAULT_PREFERENCES.speed_ms)
        log_level = data.get("log_level")
        full_output = data.get("full_output")
        browser_visible = data.get("browser_visible")
        accent_id = (
            data.get("accent_id", DEFAULT_ACCENT_ID)
            if data["schema_version"] >= 2
            else DEFAULT_ACCENT_ID
        )
        sentinel_ttl_days = data.get("sentinel_ttl_days")
        sidebar_collapsed = data.get("sidebar_collapsed")
        logs_expanded = data.get("logs_expanded")
        sentinel_logs_expanded = data.get("sentinel_logs_expanded")
        log_font_size = data.get("log_font_size")
        return GuiPreferences(
            theme=theme if isinstance(theme, str) and theme in THEMES else DEFAULT_PREFERENCES.theme,
            speed_ms=(
                speed_ms
                if type(speed_ms) is int and speed_ms in SPEED_MS_VALUES
                else DEFAULT_PREFERENCES.speed_ms
            ),
            log_level=(
                log_level
                if isinstance(log_level, str) and log_level in LOG_LEVELS
                else DEFAULT_PREFERENCES.log_level
            ),
            full_output=full_output if type(full_output) is bool else DEFAULT_PREFERENCES.full_output,
            browser_visible=(
                browser_visible
                if type(browser_visible) is bool
                else DEFAULT_PREFERENCES.browser_visible
            ),
            accent_id=(
                accent_id
                if isinstance(accent_id, str) and accent_id in ACCENT_PRESETS
                else DEFAULT_ACCENT_ID
            ),
            sentinel_ttl_days=(
                sentinel_ttl_days
                if type(sentinel_ttl_days) is int and 1 <= sentinel_ttl_days <= 365
                else None
            ),
            sidebar_collapsed=(
                sidebar_collapsed
                if type(sidebar_collapsed) is bool
                else DEFAULT_PREFERENCES.sidebar_collapsed
            ),
            logs_expanded=(
                logs_expanded if type(logs_expanded) is bool else DEFAULT_PREFERENCES.logs_expanded
            ),
            sentinel_logs_expanded=(
                sentinel_logs_expanded
                if type(sentinel_logs_expanded) is bool
                else DEFAULT_PREFERENCES.sentinel_logs_expanded
            ),
            log_font_size=(
                log_font_size
                if type(log_font_size) is int and log_font_size in LOG_FONT_SIZES
                else DEFAULT_PREFERENCES.log_font_size
            ),
        )

    def save(self, preferences: GuiPreferences) -> None:
        """Salva preferências com substituição atômica para evitar JSON parcial."""
        if preferences.theme not in THEMES:
            raise ValueError(f"Tema inválido: {preferences.theme}")
        if type(preferences.speed_ms) is not int or preferences.speed_ms not in SPEED_MS_VALUES:
            raise ValueError(f"Velocidade inválida: {preferences.speed_ms}")
        if preferences.log_level not in LOG_LEVELS:
            raise ValueError(f"Nível de log inválido: {preferences.log_level}")
        if type(preferences.log_font_size) is not int or preferences.log_font_size not in LOG_FONT_SIZES:
            raise ValueError(f"Tamanho da fonte dos logs inválido: {preferences.log_font_size}")
        if (
            type(preferences.full_output) is not bool
            or type(preferences.browser_visible) is not bool
            or type(preferences.sidebar_collapsed) is not bool
            or type(preferences.logs_expanded) is not bool
            or type(preferences.sentinel_logs_expanded) is not bool
        ):
            raise ValueError("As preferências de saída, navegador, sidebar e logs devem ser booleanas.")
        if not isinstance(preferences.accent_id, str) or preferences.accent_id not in ACCENT_PRESETS:
            raise ValueError(f"Cor predominante inválida: {preferences.accent_id}")
        if preferences.sentinel_ttl_days is not None and (
            type(preferences.sentinel_ttl_days) is not int
            or not 1 <= preferences.sentinel_ttl_days <= 365
        ):
            raise ValueError("A retenção dos runs deve ser um inteiro entre 1 e 365 dias.")

        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._path.parent,
                prefix=f".{self._path.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                json.dump(
                    {"schema_version": SCHEMA_VERSION, **asdict(preferences)},
                    stream,
                    ensure_ascii=False,
                    indent=2,
                )
                stream.write("\n")
            os.replace(temporary_path, self._path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
