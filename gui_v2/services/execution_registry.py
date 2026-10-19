"""Registro simples de execuções identificadas, independente da interface."""

from __future__ import annotations

from gui_v2.models.execution import ExecutionRecord, ExecutionState


_RUNNING_STATES = {
    ExecutionState.STARTING,
    ExecutionState.RUNNING,
    ExecutionState.PAUSE_REQUESTED,
    ExecutionState.PAUSED_BETWEEN_TESTS,
    ExecutionState.STOPPING,
}


class ExecutionRegistry:
    """Mantém registros distintos e rejeita a reutilização de uma identidade."""

    def __init__(self) -> None:
        self._records: dict[str, ExecutionRecord] = {}

    def register(self, record: ExecutionRecord) -> None:
        """Registra uma execução nova; uma colisão nunca substitui o registro."""
        self.register_batch((record,))

    def register_batch(
        self, records: tuple[ExecutionRecord, ...] | list[ExecutionRecord]
    ) -> None:
        """Valida IDs e capacidade antes de registrar o lote por inteiro."""
        if not records:
            raise ValueError("O lote de execuções não pode ser vazio.")
        ids = tuple(record.execution_id for record in records)
        if len(set(ids)) != len(ids):
            raise ValueError("O lote contém execution_id duplicado.")
        collision = next((key for key in ids if key in self._records), None)
        if collision is not None:
            raise ValueError(f"execution_id já registrado: {collision}")
        active = sum(record.state in _RUNNING_STATES for record in records)
        if len(self.running_records()) + active > 2:
            raise ValueError("A Sentinela permite no máximo duas execuções ativas.")
        if len(records) > 2:
            raise ValueError("Um lote não pode conter mais de duas execuções.")
        if len(records) == 2:
            first, second = (record.snapshot for record in records)
            if (
                first.mode != second.mode
                or first.client_key is None
                or first.client_key != second.client_key
                or first.target == second.target
                or first.count != 1
                or second.count != 1
            ):
                raise ValueError("O par exige alvos distintos do mesmo modo e cliente, sem repetição.")
        self._records.update((record.execution_id, record) for record in records)

    def get(self, execution_id: str) -> ExecutionRecord | None:
        """Devolve o registro proprietário do ID, se conhecido."""
        return self._records.get(execution_id)

    def all_records(self) -> tuple[ExecutionRecord, ...]:
        """Lista snapshots e resultados sem expor o armazenamento interno."""
        return tuple(self._records.values())

    def running_records(self) -> tuple[ExecutionRecord, ...]:
        """Lista somente registros que ainda ocupam vaga de execução."""
        return tuple(
            record
            for record in self._records.values()
            if record.state in _RUNNING_STATES
        )
