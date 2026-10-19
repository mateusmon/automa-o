"""Monta o comando da CLI e supervisiona execuções da Sentinela."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import queue
import os
import sys
from uuid import UUID, uuid4
from pathlib import Path, PureWindowsPath

import yaml

from gui_v2.models.execution import ExecutionEvent
from gui_v2.services.configuration_service import YAML_SAFE_LOADER
from gui_v2.services.process_supervisor import ProcessSupervisor
from gui_v2.models.test_item import TestItem
from gui_v2.services.sentinel_plan_service import SentinelPlan


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SENTINELA_SCRIPT = PROJECT_ROOT / "sentinela" / "sentinela.py"
SENTINELA_CONFIG = PROJECT_ROOT / "sentinela" / "config.yaml"


@dataclass(frozen=True, slots=True)
class SentinelCommand:
    """Comando pronto para a CLI e o diretório em que deve ser executado."""

    arguments: tuple[str, ...]
    cwd: Path


class SentinelRunMode(str, Enum):
    """Modos de execução disponíveis na interface da Sentinela."""

    JOURNEY = "Jornada"
    SPECIFIC_TEST = "Teste específico"


class SentinelCommandMode(str, Enum):
    """Formas tipadas de comando, incluindo o modo global restrito."""

    JOURNEY = "journey"
    SPECIFIC_TEST = "specific_test"
    ALL_CLIENTS_SPECIFIC_TEST = "all_clients_specific_test"


@dataclass(frozen=True, slots=True)
class SentinelCommandRequest:
    """Seleção tipada para montar somente combinações autorizadas da CLI."""

    mode: SentinelCommandMode
    client_key: str | None = None
    plan: SentinelPlan | None = None
    selected_tests: tuple[TestItem, ...] = ()
    available_items: tuple[TestItem, ...] = ()
    eligible_client_keys: tuple[str, ...] = ()
    items_by_client: Mapping[str, tuple[TestItem, ...]] | None = None
    count: int = 1
    ttl_days: int | None = None


class SentinelCommandService:
    """Adapta cliente e jornada selecionados para os argumentos da CLI."""

    def build(
        self, client_key: str, plan: SentinelPlan, ttl_days: int | None = None
    ) -> SentinelCommand:
        """Monta o comando somente para um plano válido e não vazio."""
        return self.build_request(
            SentinelCommandRequest(
                mode=SentinelCommandMode.JOURNEY,
                client_key=client_key,
                plan=plan,
                ttl_days=ttl_days,
            )
        )

    def build_journey_batch(
        self,
        client_key: str,
        plans: Sequence[SentinelPlan],
        ttl_days: int | None = None,
    ) -> tuple[SentinelCommand, SentinelCommand]:
        """Valida exatamente duas jornadas distintas para o mesmo cliente."""
        if len(plans) != 2:
            raise ValueError("Selecione exatamente duas jornadas.")
        if not client_key or not client_key.strip():
            raise ValueError("Informe um cliente para montar o lote da Sentinela.")
        prefixes = tuple(plan.module_prefix for plan in plans)
        if len(set(prefixes)) != 2:
            raise ValueError("As duas jornadas devem ter prefixos distintos.")
        if any(not plan.can_start for plan in plans):
            raise ValueError("As duas jornadas devem ter planos válidos e não vazios.")
        return (
            self.build(client_key, plans[0], ttl_days),
            self.build(client_key, plans[1], ttl_days),
        )

    def build_specific_test(
        self,
        client_key: str,
        test_item: TestItem,
        available_items: tuple[TestItem, ...],
        count: int = 1,
        ttl_days: int | None = None,
    ) -> SentinelCommand:
        """Monta o comando para um arquivo presente no catálogo filtrado."""
        return self.build_request(
            SentinelCommandRequest(
                mode=SentinelCommandMode.SPECIFIC_TEST,
                client_key=client_key,
                selected_tests=(test_item,),
                available_items=available_items,
                count=count,
                ttl_days=ttl_days,
            )
        )

    def build_specific_test_batch(
        self,
        client_key: str,
        test_items: tuple[TestItem, ...],
        available_items: tuple[TestItem, ...],
        ttl_days: int | None = None,
    ) -> tuple[SentinelCommand, SentinelCommand]:
        """Monta duas consultas específicas, distintas e disponíveis para um cliente."""
        if len(test_items) != 2:
            raise ValueError("Selecione exatamente dois testes específicos.")
        if len({item.path for item in test_items}) != 2:
            raise ValueError("Os dois testes específicos devem ser distintos.")
        return tuple(
            self.build_specific_test(
                client_key, item, available_items, count=1, ttl_days=ttl_days
            )
            for item in test_items
        )

    def build_all_clients_specific_test(
        self,
        test_item: TestItem,
        eligible_client_keys: Sequence[str],
        items_by_client: Mapping[str, tuple[TestItem, ...]],
        count: int = 1,
        ttl_days: int | None = None,
    ) -> SentinelCommand:
        """Monta somente a forma global restrita a um teste catalogado."""
        return self.build_request(
            SentinelCommandRequest(
                mode=SentinelCommandMode.ALL_CLIENTS_SPECIFIC_TEST,
                selected_tests=(test_item,),
                eligible_client_keys=tuple(eligible_client_keys),
                items_by_client=items_by_client,
                count=count,
                ttl_days=ttl_days,
            )
        )

    def build_request(self, request: SentinelCommandRequest) -> SentinelCommand:
        """Valida a combinação tipada antes de produzir qualquer comando CLI."""
        ttl_days = (
            self.load_ttl_default() if request.ttl_days is None else request.ttl_days
        )
        self._validate_ttl(ttl_days)
        if type(request.count) is not int or request.count not in (1, 2, 3):
            raise ValueError("A repetição deve ser 1, 2 ou 3.")

        common = [sys.executable, str(SENTINELA_SCRIPT)]
        if request.mode is SentinelCommandMode.JOURNEY:
            if not request.client_key or not request.client_key.strip():
                raise ValueError("Informe um cliente para montar o comando da Sentinela.")
            if request.plan is None or not request.plan.can_start:
                reason = request.plan.start_block_reason if request.plan else "plano ausente"
                raise ValueError(f"O plano não pode ser iniciado: {reason}.")
            if (
                request.selected_tests
                or request.available_items
                or request.eligible_client_keys
                or request.items_by_client
            ):
                raise ValueError("Jornada não aceita seleção de teste nem modo multi-cliente.")
            if request.count != 1:
                raise ValueError("--count só pode ser usado com um teste específico.")
            common.extend(("--cliente", request.client_key, "--modulo", request.plan.module_prefix))
        elif request.mode is SentinelCommandMode.SPECIFIC_TEST:
            if not request.client_key or not request.client_key.strip():
                raise ValueError("Informe um cliente para montar o comando da Sentinela.")
            if (
                request.plan is not None
                or request.eligible_client_keys
                or request.items_by_client
            ):
                raise ValueError("Teste específico de um cliente não aceita módulo ou --todos.")
            test_item = self._require_single_test(request.selected_tests)
            self._validate_test_item(test_item, request.available_items)
            common.extend(("--cliente", request.client_key, "--teste", test_item.path))
            self._append_count(common, request.count)
        elif request.mode is SentinelCommandMode.ALL_CLIENTS_SPECIFIC_TEST:
            if (
                request.client_key is not None
                or request.plan is not None
                or request.available_items
            ):
                raise ValueError("--todos não aceita cliente ou módulo de jornada.")
            test_item = self._require_single_test(request.selected_tests)
            if not request.eligible_client_keys:
                raise ValueError("O teste não está disponível em nenhum cliente.")
            if len(set(request.eligible_client_keys)) != len(request.eligible_client_keys):
                raise ValueError("A lista de clientes elegíveis contém duplicatas.")
            items_by_client = request.items_by_client or {}
            if any(
                key not in items_by_client or test_item not in items_by_client[key]
                for key in request.eligible_client_keys
            ):
                raise ValueError("A lista inclui cliente sem disponibilidade do teste no catálogo.")
            self._validate_test_item(
                test_item, items_by_client[request.eligible_client_keys[0]]
            )
            common.extend(("--todos", "--teste", test_item.path))
            self._append_count(common, request.count)
        else:
            raise ValueError(f"Modo de execução desconhecido: {request.mode!r}")

        common.extend(("--ttl", str(ttl_days)))

        if not SENTINELA_SCRIPT.is_file():
            raise FileNotFoundError(f"CLI da Sentinela não encontrada: {SENTINELA_SCRIPT}")
        return SentinelCommand(tuple(common), PROJECT_ROOT)

    @staticmethod
    def _require_single_test(selected_tests: tuple[TestItem, ...]) -> TestItem:
        if len(selected_tests) != 1:
            raise ValueError("Selecione exatamente um teste catalogado.")
        return selected_tests[0]

    @staticmethod
    def _validate_test_item(
        test_item: TestItem, available_items: tuple[TestItem, ...]
    ) -> None:
        if test_item not in available_items:
            raise ValueError("O teste selecionado não está disponível no catálogo do cliente.")
        relative_path = Path(test_item.path.replace("\\", "/"))
        windows_path = PureWindowsPath(test_item.path)
        if (
            relative_path.is_absolute()
            or windows_path.is_absolute()
            or relative_path.suffix.lower() != ".py"
            or ".." in relative_path.parts
            or ".." in windows_path.parts
            or not relative_path.parts
            or relative_path.parts[0].casefold() != "tests"
        ):
            raise ValueError("O teste deve ser um arquivo Python catalogado sob tests/.")
        tests_root = (PROJECT_ROOT / "tests").resolve()
        target = (PROJECT_ROOT / relative_path).resolve()
        try:
            target.relative_to(tests_root)
        except ValueError as error:
            raise ValueError("O caminho do teste escapa da pasta tests/.") from error
        if not target.is_file():
            raise ValueError("O teste catalogado não existe como arquivo .py.")

    @staticmethod
    def _append_count(arguments: list[str], count: int) -> None:
        if count > 1:
            arguments.extend(("--count", str(count)))

    @staticmethod
    def load_retry_limit() -> int:
        """Lê o limite de retentativas exibido na prévia da Sentinela."""
        with SENTINELA_CONFIG.open("r", encoding="utf-8") as stream:
            config = yaml.load(stream, Loader=YAML_SAFE_LOADER) or {}
        attempts = config.get("tentativas") if isinstance(config, dict) else None
        if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
            raise ValueError(
                "sentinela/config.yaml deve definir tentativas como inteiro positivo."
            )
        return attempts

    @staticmethod
    def load_ttl_default() -> int:
        """Lê o TTL padrão da configuração da Sentinela, sem alterá-la."""
        with SENTINELA_CONFIG.open("r", encoding="utf-8") as stream:
            config = yaml.load(stream, Loader=YAML_SAFE_LOADER) or {}
        ttl_days = config.get("ttl_dias") if isinstance(config, dict) else None
        SentinelCommandService._validate_ttl(ttl_days)
        return ttl_days

    @staticmethod
    def _validate_ttl(ttl_days: object) -> None:
        if (
            isinstance(ttl_days, bool)
            or not isinstance(ttl_days, int)
            or not 1 <= ttl_days <= 365
        ):
            raise ValueError("O TTL deve ser um número inteiro entre 1 e 365 dias.")


class SentinelExecutionService:
    """Executa a CLI da Sentinela com supervisão de saída e encerramento."""

    def __init__(self) -> None:
        self._supervisor = ProcessSupervisor()
        self.execution_id: str | None = None

    @property
    def supervisor(self) -> ProcessSupervisor:
        """Supervisor exclusivo associado a esta execução."""
        return self._supervisor

    def _start(
        self, command: SentinelCommand, execution_id: str | None = None
    ) -> queue.Queue[ExecutionEvent]:
        """Inicia um comando com identidade exclusiva e eventos associados."""
        execution_id = UUID(execution_id).hex if execution_id else uuid4().hex
        self.execution_id = execution_id
        env = os.environ.copy()
        pytest_addopts = env.get("PYTEST_ADDOPTS", "").strip()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTEST_ADDOPTS"] = f"{pytest_addopts} -p no:cacheprovider".strip()
        return self._supervisor.start(
            (*command.arguments, "--execution-id", execution_id),
            cwd=str(command.cwd),
            env=env,
            terminate_tree=True,
            execution_id=execution_id,
        )

    def start_command(
        self, command: SentinelCommand, execution_id: str
    ) -> queue.Queue[ExecutionEvent]:
        """Inicia um comando já validado com identidade própria."""
        return self._start(command, execution_id)

    def start(
        self,
        client_key: str,
        plan: SentinelPlan,
        ttl_days: int | None = None,
        execution_id: str | None = None,
    ) -> queue.Queue[ExecutionEvent]:
        """Inicia a jornada aprovada pelo plano e herda o ambiente atual."""
        command = SentinelCommandService().build(client_key, plan, ttl_days)
        return self._start(command, execution_id)

    def start_specific_test(
        self,
        client_key: str,
        test_item: TestItem,
        available_items: tuple[TestItem, ...],
        count: int = 1,
        ttl_days: int | None = None,
        execution_id: str | None = None,
    ) -> queue.Queue[ExecutionEvent]:
        """Inicia um único teste catalogado com a supervisão padrão."""
        command = SentinelCommandService().build_specific_test(
            client_key, test_item, available_items, count, ttl_days
        )
        return self._start(command, execution_id)

    def start_all_clients_specific_test(
        self,
        test_item: TestItem,
        eligible_client_keys: Sequence[str],
        items_by_client: Mapping[str, tuple[TestItem, ...]],
        count: int = 1,
        ttl_days: int | None = None,
        execution_id: str | None = None,
    ) -> queue.Queue[ExecutionEvent]:
        """Inicia o teste específico sequencialmente nos clientes elegíveis."""
        command = SentinelCommandService().build_all_clients_specific_test(
            test_item, eligible_client_keys, items_by_client, count, ttl_days
        )
        return self._start(command, execution_id)

    def stop(self, timeout: float | None = None) -> int | None:
        """Encerra o processo da Sentinela e sua árvore, aguardando as saídas."""
        return self._supervisor.stop(timeout)

    def wait(self, timeout: float | None = None) -> int | None:
        """Aguarda o processo e seus pipes sem pedir encerramento."""
        return self._supervisor.wait(timeout)

    @property
    def last_stop_mode(self) -> str | None:
        """Expõe se a última interrupção foi graciosa ou precisou de força."""
        return self._supervisor.last_stop_mode

    @property
    def last_stop_detail(self) -> str | None:
        """Expõe o motivo diagnóstico da última interrupção."""
        return self._supervisor.last_stop_detail
