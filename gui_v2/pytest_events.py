"""Eventos de progresso ativados somente pelo launcher Pytest da GUI v2."""

from __future__ import annotations

import json
import sys


EVENT_PREFIX = "ASI_GUI_PYTEST:"
_results: dict[str, str] = {}


def _publish(kind: str, **fields: object) -> None:
    """Separa o marcador de linhas parciais produzidas por -v/-s."""
    sys.stdout.write("\n" + EVENT_PREFIX + json.dumps({"type": kind, **fields}, ensure_ascii=True) + "\n")
    sys.stdout.flush()


def pytest_collection_finish(session) -> None:
    """Publica a quantidade efetivamente selecionada, após deselections."""
    _results.clear()
    _publish("COLLECTION_COMPLETED", count=len(session.items))


def pytest_runtest_logstart(nodeid: str, location) -> None:
    """Informa o alvo antes das fixtures e do corpo do teste."""
    _results.pop(nodeid, None)
    _publish("TEST_STARTED", target=nodeid)


def pytest_runtest_logreport(report) -> None:
    """Consolida setup/call/teardown para não contar o mesmo teste duas vezes."""
    previous = _results.get(report.nodeid, "PASSED")
    if report.failed:
        result = "FAILED" if report.when == "call" else "ERROR"
    elif report.skipped:
        result = "SKIPPED"
    else:
        result = "PASSED"
    severity = {"PASSED": 0, "SKIPPED": 1, "FAILED": 2, "ERROR": 3}
    _results[report.nodeid] = max((previous, result), key=severity.__getitem__)
    if report.when == "teardown":
        _publish("TEST_RESULT", target=report.nodeid, result=_results.pop(report.nodeid))
