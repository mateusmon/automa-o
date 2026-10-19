"""Leitura do último histórico de testes, sem modificar os arquivos de origem."""

from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HISTORY_DIR = PROJECT_ROOT / "historico_testes" / "estado_atual"
_RESULT_SEVERITY = {"pass": 0, "skip": 1, "fail": 2}


class HistoryService:
    """Lê o snapshot de histórico associado a um cliente."""

    def __init__(self, history_dir: Path = DEFAULT_HISTORY_DIR) -> None:
        self._history_dir = history_dir

    def load_for_client(self, client_key: str | None) -> dict[str, dict[str, Any]]:
        """Retorna o histórico válido do cliente ou um mapeamento vazio."""
        if (
            not isinstance(client_key, str)
            or not client_key
            or client_key != client_key.strip()
        ):
            return {}

        try:
            history_root = self._history_dir.resolve()
            history_path = (self._history_dir / f"{client_key}.json").resolve()
            if history_path.parent != history_root or not history_path.is_file():
                return {}
            with history_path.open(encoding="utf-8") as stream:
                data: Any = json.load(stream)
        except (OSError, UnicodeDecodeError, ValueError, RecursionError):
            return {}

        if not isinstance(data, Mapping):
            return {}
        if any(
            not isinstance(key, str) or not isinstance(value, Mapping)
            for key, value in data.items()
        ):
            return {}
        if any(not isinstance(value.get("resultado"), str) for value in data.values()):
            return {}

        return {key: dict(value) for key, value in data.items()}

    @staticmethod
    def aggregate_by_test_path(
        history: Mapping[str, Mapping[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Agrupa nodeids por arquivo e conserva o resultado de maior severidade."""
        aggregated: dict[str, dict[str, Any]] = {}
        for nodeid, entry in history.items():
            test_path = nodeid.split("::", maxsplit=1)[0]
            current = aggregated.get(test_path)
            new_severity = _RESULT_SEVERITY.get(entry.get("resultado"), -1)
            current_severity = (
                _RESULT_SEVERITY.get(current.get("resultado"), -1)
                if current is not None
                else -1
            )
            if current is None or new_severity >= current_severity:
                aggregated[test_path] = dict(entry)
        return aggregated
