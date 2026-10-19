"""Modelos de domínio da nova interface."""

from gui_v2.models.app_state import AppState
from gui_v2.models.execution import (
    ExecutionEvent,
    ExecutionEventLevel,
    ExecutionEventType,
    ExecutionProgress,
    ExecutionState,
)
from gui_v2.models.test_item import TestItem

__all__ = [
    "AppState",
    "ExecutionEvent",
    "ExecutionEventLevel",
    "ExecutionEventType",
    "ExecutionProgress",
    "ExecutionState",
    "TestItem",
]
