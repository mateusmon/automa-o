"""Abre o Playwright Codegen sem acoplar processo e validação à interface."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CodegenService:
    """Valida a URL e inicia o Codegen em um processo independente."""

    def __init__(self, project_root: Path = PROJECT_ROOT) -> None:
        self._project_root = project_root

    def launch(self, url: str) -> subprocess.Popen:
        """Inicia ``playwright codegen`` para uma URL HTTP ou HTTPS válida."""
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Informe uma URL HTTP ou HTTPS válida.")

        return subprocess.Popen(
            [sys.executable, "-m", "playwright", "codegen", url],
            cwd=self._project_root,
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
            ),
        )
