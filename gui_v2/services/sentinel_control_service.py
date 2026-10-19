"""Canal de controle identificado para uma execução da Sentinela."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import threading
from uuid import UUID

from gui_v2.services.sentinel_artifact_service import REPORTS_ROOT


_COMMANDS = {"pause", "resume", "stop"}
_SCHEMA_VERSION = 1
_CONTROL_LOCK = threading.Lock()


class SentinelControlService:
    """Grava comandos atômicos somente no run que pertence ao execution_id."""

    @staticmethod
    def control_path(run_directory: Path, execution_id: str) -> Path:
        """Valida o dono do run e devolve o caminho exclusivo de controle."""
        normalized_id = UUID(execution_id).hex
        resolved_root = REPORTS_ROOT.resolve(strict=False)
        if run_directory.is_symlink():
            raise ValueError("A pasta do run não pode ser um symlink.")
        resolved_run = run_directory.resolve(strict=True)
        try:
            resolved_run.relative_to(resolved_root)
        except ValueError as error:
            raise ValueError("A pasta do run está fora de sentinela/reports.") from error
        if not resolved_run.is_dir() or not (
            resolved_run.name.endswith(f"_{normalized_id[:8]}")
            or resolved_run.name.endswith(f"_{normalized_id}")
        ):
            raise ValueError("A pasta do run não pertence a esta execução.")
        owner_file = resolved_run / ".execution-id"
        if owner_file.is_symlink() or owner_file.read_text(encoding="ascii") != normalized_id:
            raise ValueError("O marcador do run não confirma o dono da execução.")
        return resolved_root / f".gui-control-{normalized_id}.json"

    def write_command(
        self, run_directory: Path, execution_id: str, command: str
    ) -> Path:
        """Grava pause/resume/stop atomicamente; stop não pode ser revertido."""
        if command not in _COMMANDS:
            raise ValueError("Comando de controle inválido.")
        normalized_id = UUID(execution_id).hex
        destination = self.control_path(run_directory, normalized_id)
        with _CONTROL_LOCK:
            if destination.is_symlink():
                raise ValueError("O arquivo de controle não pode ser um symlink.")
            if destination.exists():
                try:
                    previous = json.loads(destination.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError):
                    previous = None
                if isinstance(previous, dict) and previous.get("command") == "stop":
                    if command != "stop":
                        raise RuntimeError("A execução já recebeu um comando de parada.")
                    return destination

            payload = json.dumps(
                {
                    "schema_version": _SCHEMA_VERSION,
                    "execution_id": normalized_id,
                    "command": command,
                },
                ensure_ascii=True,
                separators=(",", ":"),
            )
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".gui-control-{normalized_id}-",
                suffix=".tmp",
                dir=destination.parent,
            )
            temporary_path = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary_path, destination)
            finally:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
            return destination

    @staticmethod
    def remove_command(execution_id: str) -> None:
        """Remove o canal da execução depois que seu processo chega ao terminal."""
        normalized_id = UUID(execution_id).hex
        path = REPORTS_ROOT.resolve(strict=False) / f".gui-control-{normalized_id}.json"
        with _CONTROL_LOCK:
            if path.is_symlink():
                return
            path.unlink(missing_ok=True)
