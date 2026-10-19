"""Estado de domínio compartilhado pela nova interface."""

from __future__ import annotations

from dataclasses import dataclass, field

from gui_v2.models.execution import ExecutionState


@dataclass(slots=True)
class AppState:
    """Dados da interface, sem referências a widgets ou serviços.

    Os identificadores em ``selected_test_ids`` são os ``selection_id`` de
    :class:`gui_v2.models.test_item.TestItem`: um path ou um nodeid do Pytest.
    ``execution_state`` representa o ciclo de vida da execução corrente.
    """

    current_page: str = "Execução"
    theme: str = "Sistema"
    client_key: str | None = None
    url: str = ""
    speed_ms: int = 0
    current_module: str = "Almoxarifado"
    selected_test_ids: set[str] = field(default_factory=set)
    execution_state: ExecutionState = ExecutionState.IDLE
