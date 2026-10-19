"""Modelos tipados para estado e eventos de uma execução da GUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING
import queue
import time

if TYPE_CHECKING:
    from gui_v2.services.process_supervisor import ProcessMetrics


class ExecutionState(StrEnum):
    """Estados do ciclo de vida de uma execução."""

    IDLE = "IDLE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSE_REQUESTED = "PAUSE_REQUESTED"
    PAUSED_BETWEEN_TESTS = "PAUSED_BETWEEN_TESTS"
    STOPPING = "STOPPING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    INTERRUPTED = "INTERRUPTED"


class ExecutionEventType(StrEnum):
    """Origem/tipo do conteúdo publicado durante uma execução."""

    STDOUT = "STDOUT"
    STDERR = "STDERR"
    PROCESS_EXITED = "PROCESS_EXITED"
    EXECUTION_STARTED = "EXECUTION_STARTED"
    TEST_STARTED = "TEST_STARTED"
    TEST_RESULT = "TEST_RESULT"
    PYTEST_SUMMARY = "PYTEST_SUMMARY"
    EXECUTION_FINISHED = "EXECUTION_FINISHED"
    COLLECTION_COMPLETED = "COLLECTION_COMPLETED"


class ExecutionEventLevel(StrEnum):
    """Níveis de severidade/apresentação dos eventos."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class ExecutionEvent:
    """Evento independente de UI emitido por uma execução.

    Se omitido, ``timestamp`` captura o instante de criação em UTC.
    """

    event_type: ExecutionEventType
    level: ExecutionEventLevel
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    return_code: int | None = None
    target: str | None = None
    raw_message: str | None = None
    count: int | None = None
    monotonic_time: float | None = None
    execution_id: str | None = None


def event_belongs_to_execution(
    event: ExecutionEvent, execution_id: str | None
) -> bool:
    """Indica se um evento ainda pertence à execução selecionada pelo controlador."""
    return execution_id is not None and event.execution_id == execution_id


@dataclass(frozen=True, slots=True)
class ExecutionSnapshot:
    """Seleção imutável capturada no momento em que a execução começa."""

    client_key: str | None
    mode: str
    target: str
    count: int
    ttl_days: int
    options: tuple[str, ...] = ()


@dataclass(slots=True)
class ExecutionRecord:
    """Estado e recursos de uma execução, sem dependência de widgets."""

    execution_id: str
    snapshot: ExecutionSnapshot
    events: queue.Queue[ExecutionEvent]
    supervisor: object
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state: ExecutionState = ExecutionState.RUNNING
    output: list[str] = field(default_factory=list)
    artifact_paths: list[Path] = field(default_factory=list)
    finished_at: datetime | None = None
    metrics: ProcessMetrics | None = None


@dataclass(slots=True)
class ExecutionProgress:
    """Progresso reconhecido da execução, independente da interface."""

    total_targets: int
    completed_targets: int = 0
    current_target: str | None = None
    started_at: float | None = None
    finished_at: float | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Duração monotônica somente quando os dois marcos são conhecidos."""
        if self.started_at is None:
            return None
        end = self.finished_at if self.finished_at is not None else time.monotonic()
        return max(0.0, end - self.started_at)
