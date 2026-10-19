"""Localiza artefatos de uma execução a partir da saída da Sentinela."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import sys
import webbrowser
from collections.abc import Sequence
from datetime import datetime, timedelta
from uuid import UUID


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_ROOT = (PROJECT_ROOT / "sentinela" / "reports").resolve()
REPORTS_PATH = PROJECT_ROOT / "sentinela" / "reports"
_RUN_PATTERN = re.compile(r"Run salvo em(?:\s+\[([0-9a-fA-F]{32})\])?:\s*(.+?)\s*$", re.IGNORECASE)
_REPORT_PATTERN = re.compile(r"Relat[oó]rio\s*:\s*(.+?)\s*$", re.IGNORECASE)
_RUN_DIRECTORY_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2})_(\d{2}h\d{2}(?:\d{2})?)_"
)
MAX_HISTORY_RUNS = 20


@dataclass(frozen=True, slots=True)
class SentinelHistoryRun:
    """Run histórico validado e seus artefatos locais."""

    execution_id: str
    target: str
    state: str
    folder_path: Path
    report_path: Path | None
    trace_paths: tuple[Path, ...]
    started_at: datetime


@dataclass(frozen=True, slots=True)
class SentinelRunArtifacts:
    """Relatório e pasta confirmados para uma execução concluída."""

    report_path: Path | None
    folder_path: Path | None
    trace_paths: tuple[Path, ...] = ()


class SentinelArtifactService:
    """Valida e abre somente artefatos existentes sob ``sentinela/reports``."""

    @staticmethod
    def mentions_artifacts(line: str) -> bool:
        """Indica se a linha anuncia pasta ou relatório e exige nova localização."""
        return bool(_RUN_PATTERN.search(line) or _REPORT_PATTERN.search(line))

    def locate(
        self, output_lines: Sequence[str], execution_id: str | None = None
    ) -> SentinelRunArtifacts:
        """Extrai paths da saída e ignora caminhos fora da pasta de relatórios."""
        run_directory: Path | None = None
        report_path: Path | None = None
        for line in output_lines:
            run_match = _RUN_PATTERN.search(line)
            report_match = _REPORT_PATTERN.search(line)
            if run_match:
                reported_id, raw_path = run_match.groups()
                if execution_id is not None and reported_id != execution_id:
                    continue
                run_directory = self._resolve(raw_path.rstrip("/\\"))
            if report_match:
                report_path = self._resolve(report_match.group(1))

        if run_directory is not None and not run_directory.is_dir():
            run_directory = None
        if run_directory is not None and execution_id is not None:
            if not (
                run_directory.name.endswith(f"_{execution_id[:8]}")
                or run_directory.name.endswith(f"_{execution_id}")
            ):
                run_directory = None
            else:
                owner_path = run_directory / ".execution-id"
                try:
                    owner_id = (
                        UUID(owner_path.read_text(encoding="ascii").strip()).hex
                        if not owner_path.is_symlink()
                        else None
                    )
                except (OSError, UnicodeError):
                    owner_id = None
                except ValueError:
                    owner_id = None
                if owner_id != execution_id:
                    run_directory = None
        if report_path is not None and not report_path.is_file():
            report_path = None
        if report_path is not None and run_directory is not None:
            if report_path.parent != run_directory:
                report_path = None
        if execution_id is not None and run_directory is None:
            report_path = None
        if report_path is None and run_directory is not None:
            candidate = self._resolve(str(run_directory / "report.html"))
            if candidate is not None and candidate.parent == run_directory and candidate.is_file():
                report_path = candidate
        traces = self.list_traces(run_directory) if run_directory is not None else ()
        return SentinelRunArtifacts(report_path, run_directory, traces)

    def discover_history(
        self, limit: int = MAX_HISTORY_RUNS, ttl_days: int | None = None
    ) -> tuple[SentinelHistoryRun, ...]:
        """Descobre os runs mais recentes com ID e proprietário válidos."""
        if type(limit) is not int or limit < 1:
            raise ValueError("O limite do histórico deve ser um inteiro positivo.")
        if ttl_days is not None and (
            type(ttl_days) is not int or not 1 <= ttl_days <= 365
        ):
            raise ValueError("O TTL do histórico deve ser um inteiro entre 1 e 365 dias.")
        if not self._reports_root_is_trusted():
            return ()

        cutoff = datetime.now() - timedelta(days=ttl_days) if ttl_days is not None else None
        candidates: list[tuple[datetime, float, str, str, Path]] = []
        for directory in REPORTS_ROOT.iterdir():
            if directory.is_symlink() or not directory.is_dir():
                continue
            owner_path = directory / ".execution-id"
            if owner_path.is_symlink() or not owner_path.is_file():
                continue
            try:
                execution_id = UUID(owner_path.read_text(encoding="ascii").strip()).hex
                resolved_directory = directory.resolve(strict=True)
                resolved_directory.relative_to(REPORTS_ROOT)
                modified_timestamp = directory.stat().st_mtime
            except (OSError, UnicodeError, ValueError):
                continue
            folder_name = directory.name.casefold()
            if not (
                folder_name.endswith(f"_{execution_id[:8]}")
                or folder_name.endswith(f"_{execution_id}")
            ):
                continue
            run_started_at = self._run_started_at(directory.name)
            if cutoff is not None and (run_started_at is None or run_started_at < cutoff):
                continue
            if run_started_at is None:
                run_started_at = datetime.fromtimestamp(modified_timestamp).astimezone().replace(
                    tzinfo=None
                )

            target = directory.name
            match = re.match(
                r"^\d{4}-\d{2}-\d{2}_\d{2}h\d{2}(?:\d{2})?_(.+)_([0-9a-fA-F]{8}|[0-9a-fA-F]{32})$",
                target,
            )
            if match:
                target = match.group(1).replace("_", " ")
            candidates.append(
                (run_started_at, modified_timestamp, execution_id, target, resolved_directory)
            )

        runs: list[SentinelHistoryRun] = []
        accepted_ids: set[str] = set()
        for started_at, _modified_timestamp, execution_id, target, resolved_directory in sorted(
            candidates, key=lambda item: (item[0], item[1]), reverse=True
        ):
            if len(runs) >= limit:
                break
            if execution_id in accepted_ids:
                continue
            artifacts = self.locate(
                (f"Run salvo em [{execution_id}]: {resolved_directory}",), execution_id
            )
            if artifacts.folder_path != resolved_directory:
                continue
            report_failed = self.report_has_failures(artifacts.report_path)
            if artifacts.report_path is None:
                state = "SEM RELATÓRIO"
            elif report_failed is True:
                state = "COM FALHAS"
            elif report_failed is False:
                state = "SEM FALHAS DETECTADAS"
            else:
                state = "RELATÓRIO DISPONÍVEL"
            runs.append(
                SentinelHistoryRun(
                    execution_id=execution_id,
                    target=target,
                    state=state,
                    folder_path=resolved_directory,
                    report_path=artifacts.report_path,
                    trace_paths=artifacts.trace_paths,
                    started_at=started_at,
                )
            )
            accepted_ids.add(execution_id)
        return tuple(runs)

    @staticmethod
    def read_history_output(run: SentinelHistoryRun) -> tuple[str, ...]:
        """Forma saída breve para um item de histórico a partir do relatório."""
        lines = [
            f"Run histórico · {run.target}",
            f"Execution ID: {run.execution_id}",
            f"Iniciado em: {run.started_at:%d/%m/%Y %H:%M:%S}",
            f"Pasta: {run.folder_path}",
        ]
        if run.report_path is None:
            lines.append("Resultado indisponível: este run não possui relatório.")
            return tuple(lines)
        lines.append(f"Relatório: {run.report_path}")
        try:
            with run.report_path.open(encoding="utf-8", errors="replace") as stream:
                content = stream.read(65_536)
        except OSError:
            lines.append("Não foi possível ler o relatório.")
            return tuple(lines)
        summary = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        if summary:
            title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", summary.group(1))).strip()
            if title:
                lines.append(f"Resumo: {title[:300]}")
        return tuple(lines)

    @staticmethod
    def _reports_root_is_trusted() -> bool:
        """Aceita somente sentinela/reports dentro da raiz real do projeto."""
        try:
            if REPORTS_PATH.is_symlink():
                return False
            resolved_root = REPORTS_PATH.resolve(strict=True)
            resolved_root.relative_to(PROJECT_ROOT)
            return resolved_root == REPORTS_ROOT and resolved_root.is_dir()
        except (OSError, ValueError):
            return False

    @staticmethod
    def _run_started_at(directory_name: str) -> datetime | None:
        """Lê os formatos de timestamp de run aceitos pela retenção da engine."""
        match = _RUN_DIRECTORY_PATTERN.match(directory_name)
        if match is None:
            return None
        date_part, time_part = match.groups()
        time_formats = ("%Hh%M", "%Hh%M%S")
        for time_format in time_formats:
            try:
                return datetime.strptime(f"{date_part}_{time_part}", f"%Y-%m-%d_{time_format}")
            except ValueError:
                continue
        return None

    def list_traces(self, run_directory: Path | None) -> tuple[Path, ...]:
        """Lista traces ZIP diretos do run validado, ignorando symlinks e escapes."""
        if run_directory is None:
            return ()
        if run_directory.is_symlink():
            return ()
        resolved_run = self._resolve(str(run_directory))
        if resolved_run is None or not resolved_run.is_dir():
            return ()
        traces: list[Path] = []
        for candidate in resolved_run.glob("*_trace.zip"):
            if candidate.is_symlink():
                continue
            try:
                resolved = candidate.resolve(strict=True)
                resolved.relative_to(resolved_run)
            except (OSError, ValueError):
                continue
            if resolved.is_file() and resolved.suffix.casefold() == ".zip":
                traces.append(resolved)
        return tuple(sorted(traces, key=lambda path: path.name.casefold()))

    @staticmethod
    def report_has_failures(report_path: Path | None) -> bool | None:
        """Detecta falhas Pytest no relatório quando a CLI terminou com código zero."""
        if report_path is None or report_path.is_symlink():
            return None
        try:
            content = report_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return None
        counts = re.findall(
            r'<span class="badge (?:falhou|retentou_falhou)">[^<]*?(\d+)',
            content,
        )
        return any(int(count) > 0 for count in counts) if counts else None

    def open_trace(self, trace_path: Path, run_directory: Path | None) -> None:
        """Abre manualmente um trace que ainda pertença ao run atual validado."""
        if run_directory is None:
            raise ValueError("Não há pasta de execução validada para este trace.")
        if run_directory.is_symlink():
            raise ValueError("Não é permitido abrir um trace por symlink de run.")
        resolved_run = self._resolve(str(run_directory))
        resolved_trace = self._resolve(str(trace_path))
        if resolved_run is None or resolved_trace is None or not resolved_run.is_dir():
            raise ValueError("O run ou trace não pertence a sentinela/reports.")
        if trace_path.is_symlink():
            raise ValueError("Não é permitido abrir um trace por symlink.")
        try:
            resolved_trace.relative_to(resolved_run)
        except ValueError as error:
            raise ValueError("O trace não pertence ao run atual.") from error
        if (
            resolved_trace.suffix.casefold() != ".zip"
            or not resolved_trace.name.endswith("_trace.zip")
            or not resolved_trace.is_file()
            or resolved_trace not in self.list_traces(resolved_run)
        ):
            raise FileNotFoundError(f"Trace indisponível: {trace_path}")
        subprocess.Popen(
            [sys.executable, "-m", "playwright", "show-trace", str(resolved_trace)],
            cwd=str(PROJECT_ROOT),
        )

    @staticmethod
    def _resolve(raw_path: str) -> Path | None:
        if not SentinelArtifactService._reports_root_is_trusted():
            return None
        candidate = Path(raw_path.strip().strip('"'))
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        try:
            resolved = candidate.resolve(strict=False)
            resolved.relative_to(REPORTS_ROOT)
        except (OSError, ValueError):
            return None
        return resolved

    @staticmethod
    def open_report(path: Path) -> None:
        """Abre o relatório HTML existente no navegador padrão."""
        if path.is_symlink():
            raise ValueError("Não é permitido abrir relatório por symlink.")
        resolved = SentinelArtifactService._resolve(str(path))
        if resolved is None or resolved != path.resolve(strict=False):
            raise ValueError("Relatório fora da pasta de runs validada.")
        if not resolved.is_file():
            raise FileNotFoundError(f"Relatório não encontrado: {path}")
        if not webbrowser.open(resolved.as_uri()):
            raise OSError("Não foi possível abrir o relatório no navegador padrão.")

    @staticmethod
    def open_folder(path: Path) -> None:
        """Abre a pasta existente no gerenciador de arquivos."""
        if path.is_symlink():
            raise ValueError("Não é permitido abrir run por symlink.")
        resolved = SentinelArtifactService._resolve(str(path))
        if resolved is None or resolved != path.resolve(strict=False):
            raise ValueError("Pasta fora da raiz de relatórios validada.")
        if not resolved.is_dir():
            raise FileNotFoundError(f"Pasta da execução não encontrada: {path}")
        if os.name == "nt":
            subprocess.Popen(["explorer.exe", str(resolved)])
        else:
            subprocess.Popen(["xdg-open", str(resolved)])
