"""Adapta uma seleção ordenada de testes para execução pelo Pytest."""

from __future__ import annotations

from collections.abc import Sequence
import os
import json
import queue
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gui_v2.models.execution import (
    ExecutionEvent,
    ExecutionEventLevel,
    ExecutionEventType,
    ExecutionState,
)
from gui_v2.services.preferences_service import SPEED_MS_VALUES
from gui_v2.services.process_supervisor import ProcessSupervisor
from gui_v2.pytest_events import EVENT_PREFIX


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PytestService:
    """Inicia uma seleção ordenada de alvos do Pytest."""

    def __init__(self) -> None:
        self._supervisor = ProcessSupervisor()
        self._adaptation_done = threading.Event()
        self._adaptation_done.set()

    def start(
        self,
        targets: Sequence[str] | str,
        speed_ms: int = 0,
        browser_visible: bool = True,
        client_key: str | None = None,
    ) -> queue.Queue[ExecutionEvent]:
        """Executa os alvos na ordem recebida e para na primeira falha."""
        if isinstance(targets, str):
            targets = (targets,)
        if not targets or any(
            not isinstance(target, str) or not target.strip() for target in targets
        ):
            raise ValueError("Informe ao menos um alvo válido do Pytest.")
        if type(speed_ms) is not int or speed_ms not in SPEED_MS_VALUES:
            raise ValueError(f"Velocidade inválida: {speed_ms}")
        if type(browser_visible) is not bool:
            raise ValueError("A visibilidade do navegador deve ser booleana.")
        if client_key is not None and (not isinstance(client_key, str) or not client_key.strip()):
            raise ValueError("Informe uma chave de cliente válida.")
        command = [sys.executable, "-m", "pytest", "-x", "-v", "-s", "-p", "no:randomly", "-p", "gui_v2.pytest_events"]
        if not browser_visible:
            command.append("--headless")
        command.extend(targets)
        raw_events = self._supervisor.start(
            command,
            cwd=str(PROJECT_ROOT),
            env={
                **os.environ,
                "ASI_SLOW_MO": str(speed_ms),
                "ASI_PAUSAR_NA_FALHA": "1",
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUNBUFFERED": "1",
                **({"ASI_CLIENTE_ATIVO": client_key} if client_key is not None else {}),
            },
            terminate_tree=True,
        )
        events: queue.Queue[ExecutionEvent] = queue.Queue()
        self._adaptation_done = threading.Event()
        events.put(ExecutionEvent(
            ExecutionEventType.EXECUTION_STARTED,
            ExecutionEventLevel.INFO,
            f"Execução iniciada: {len(targets)} alvo(s).",
        ))
        threading.Thread(
            target=self._adapt_events_and_signal,
            args=(raw_events, events, self._adaptation_done, True),
            name="pytest-event-adapter",
            daemon=True,
        ).start()
        return events

    @staticmethod
    def _adapt_events(
        source: queue.Queue[ExecutionEvent], events: queue.Queue[ExecutionEvent],
        structured: bool = False,
    ) -> None:
        """Converte a saída -v do Pytest em eventos sem descartar blocos originais."""
        summary_result_pattern = re.compile(r"\b\d+\s+(?:passed|failed|skipped|error|errors|xfailed|xpassed)\b")
        collected_pattern = re.compile(r"\bcollected\s+(?P<count>\d+)\s+items?\b")
        result_pattern = re.compile(r"^(?P<target>.+?)\s+(?P<result>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)(?:\s|$)")
        failed_pattern = re.compile(r"^(?P<result>FAILED|ERROR)\s+(?P<detail>.+)$")
        traceback_line_pattern = re.compile(r"^\s*(?:E(?:\s|$)|>\s)")
        warning_line_pattern = re.compile(
            r"\b(?:DeprecationWarning|PendingDeprecationWarning|FutureWarning|"
            r"UserWarning|RuntimeWarning|ResourceWarning|PytestWarning|Warning):"
        )
        reported_targets: set[str] = set()
        pending: list[ExecutionEvent] = []

        def publish_ready(force: bool = False) -> None:
            cutoff = datetime.now(timezone.utc) - timedelta(milliseconds=40)
            ready = [item for item in pending if force or item.timestamp <= cutoff]
            if not ready:
                return
            ready_ids = {id(item) for item in ready}
            pending[:] = [item for item in pending if id(item) not in ready_ids]
            for item in sorted(ready, key=lambda value: value.timestamp):
                events.put(item)

        while True:
            try:
                event = source.get(timeout=0.025)
            except queue.Empty:
                publish_ready()
                continue
            if event.event_type is ExecutionEventType.PROCESS_EXITED:
                publish_ready(force=True)
                events.put(event)
                return

            message = event.message
            if event.event_type is ExecutionEventType.STDOUT:
                if structured and message.startswith(EVENT_PREFIX):
                    try:
                        payload = json.loads(message[len(EVENT_PREFIX):])
                        kind = ExecutionEventType(payload["type"])
                        if kind is ExecutionEventType.COLLECTION_COMPLETED and type(payload.get("count")) is int:
                            adapted = ExecutionEvent(kind, ExecutionEventLevel.INFO, "Testes coletados pelo Pytest.", event.timestamp, count=payload["count"], monotonic_time=time.monotonic())
                        elif kind is ExecutionEventType.TEST_STARTED and isinstance(payload.get("target"), str):
                            adapted = ExecutionEvent(kind, ExecutionEventLevel.INFO, "Teste iniciado.", event.timestamp, target=payload["target"])
                        elif kind is ExecutionEventType.TEST_RESULT and isinstance(payload.get("target"), str) and payload.get("result") in {"PASSED", "SKIPPED", "FAILED", "ERROR"}:
                            result = payload["result"]
                            level = ExecutionEventLevel.ERROR if result in {"FAILED", "ERROR"} else ExecutionEventLevel.WARNING if result == "SKIPPED" else ExecutionEventLevel.INFO
                            adapted = ExecutionEvent(kind, level, result, event.timestamp, target=payload["target"])
                        else:
                            raise ValueError("Evento Pytest inválido")
                    except (ValueError, KeyError, TypeError):
                        pass  # Preserva a linha original quando o marcador é inválido.
                    else:
                        pending.append(adapted)
                        publish_ready()
                        continue
                collected_match = collected_pattern.search(message)
                if collected_match and not structured:
                    pending.append(ExecutionEvent(
                        ExecutionEventType.COLLECTION_COMPLETED,
                        ExecutionEventLevel.INFO,
                        "Testes coletados pelo Pytest.",
                        event.timestamp,
                        count=int(collected_match.group("count")),
                        raw_message=message,
                        monotonic_time=time.monotonic(),
                    ))
                    publish_ready()
                    continue
                if message.startswith("collecting ") or message.startswith("collected "):
                    pending.append(ExecutionEvent(
                        event.event_type,
                        event.level,
                        message,
                        event.timestamp,
                        raw_message=message,
                    ))
                    publish_ready()
                    continue
                match = result_pattern.match(message)
                if not match:
                    failed_match = failed_pattern.match(message)
                    if failed_match:
                        detail = failed_match.group("detail")
                        if detail.startswith("at setup of ") or detail.startswith("at teardown of "):
                            target = detail.split(" of ", 1)[1].split()[0]
                        else:
                            target = detail.split()[0]
                        if "::" in target:
                            match = re.match(
                                r"^(?P<target>.+?)\s+(?P<result>FAILED|ERROR)$",
                                f"{target} {failed_match.group('result')}",
                            )
                if match and "::" not in match.group("target"):
                    match = None
                if match and not structured:
                    target = match.group("target")
                    result = match.group("result")
                    if target in reported_targets:
                        pending.append(ExecutionEvent(
                            event.event_type,
                            ExecutionEventLevel.INFO,
                            message,
                            event.timestamp,
                            raw_message=message,
                        ))
                        publish_ready()
                        continue
                    reported_targets.add(target)
                    level = (ExecutionEventLevel.ERROR if result in {"FAILED", "ERROR", "XPASS"}
                             else ExecutionEventLevel.WARNING if result == "SKIPPED"
                             else ExecutionEventLevel.INFO)
                    pending.append(ExecutionEvent(ExecutionEventType.TEST_RESULT, level, result, event.timestamp, target=target, raw_message=message))
                    publish_ready()
                    continue
                if message.startswith("=") and summary_result_pattern.search(message):
                    summary_level = (
                        ExecutionEventLevel.ERROR
                        if " failed" in message or " error" in message
                        else ExecutionEventLevel.WARNING
                        if " skipped" in message
                        else ExecutionEventLevel.INFO
                    )
                    pending.append(ExecutionEvent(ExecutionEventType.PYTEST_SUMMARY, summary_level, message, event.timestamp, raw_message=message))
                    publish_ready()
                    continue
                if message.startswith("================") and "warnings summary" in message.lower():
                    pending.append(ExecutionEvent(
                        event.event_type, ExecutionEventLevel.WARNING, message,
                        event.timestamp, raw_message=message,
                    ))
                elif message.startswith("================") and (
                    "FAILURES" in message or "ERRORS" in message
                ):
                    pending.append(ExecutionEvent(
                        event.event_type, ExecutionEventLevel.ERROR, message,
                        event.timestamp, raw_message=message,
                    ))
                elif message.startswith(("WARNING", "ERROR", "INTERNALERROR")):
                    level = ExecutionEventLevel.ERROR if "ERROR" in message else ExecutionEventLevel.WARNING
                    pending.append(ExecutionEvent(ExecutionEventType.STDOUT, level, message, event.timestamp, raw_message=message))
                else:
                    # Mantém toda a saída original, inclusive linhas vazias de tracebacks.
                    level = (
                        ExecutionEventLevel.ERROR
                        if traceback_line_pattern.match(message)
                        else ExecutionEventLevel.WARNING
                        if warning_line_pattern.search(message)
                        else event.level
                    )
                    pending.append(ExecutionEvent(event.event_type, level, message, event.timestamp, raw_message=message))
                publish_ready()
                continue
            if event.event_type is ExecutionEventType.STDERR:
                pending.append(ExecutionEvent(event.event_type, event.level, message, event.timestamp, raw_message=message))
                publish_ready()

    def stop(self, timeout: float | None = None) -> int | None:
        """Encerra o Pytest e aguarda a publicação de todos os eventos adaptados."""
        deadline = None if timeout is None else time.monotonic() + timeout
        return_code = self._supervisor.stop(timeout)
        remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
        if not self._adaptation_done.wait(remaining):
            raise subprocess.TimeoutExpired("pytest event adapter", timeout)
        return return_code

    @property
    def last_stop_mode(self) -> str | None:
        """Distingue cancelamento efetivo de processo já concluído."""
        return self._supervisor.last_stop_mode

    @classmethod
    def _adapt_events_and_signal(
        cls,
        source: queue.Queue[ExecutionEvent],
        events: queue.Queue[ExecutionEvent],
        done: threading.Event,
        structured: bool = False,
    ) -> None:
        """Sinaliza mesmo se a transformação terminar com erro inesperado."""
        try:
            cls._adapt_events(source, events, structured)
        finally:
            done.set()

    @staticmethod
    def classify_outcome(return_code: int | None, skipped: bool, passed: bool = False) -> ExecutionState:
        """Converte o código Pytest e marcador de skip no estado da execução."""
        if return_code != 0:
            return ExecutionState.FAILED
        return ExecutionState.SKIPPED if skipped and not passed else ExecutionState.SUCCEEDED
