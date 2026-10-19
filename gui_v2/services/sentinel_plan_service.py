"""Disponibiliza jornadas lógicas da Sentinela para um cliente."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

from gui_v2.services.catalog_service import CatalogService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SENTINELA_DIR = PROJECT_ROOT / "sentinela"
ORDEM_PATH = SENTINELA_DIR / "ordem.yaml"


@dataclass(frozen=True, slots=True)
class SentinelModule:
    """Prefixo lógico selecionável da ordem da Sentinela."""

    path: str
    parent_path: str | None
    explicit_only: bool
    occurrence_count: int


@dataclass(frozen=True, slots=True)
class SentinelPlanOccurrence:
    """Uma ocorrência executável da jornada, com sua ordem preservada."""

    index: int
    path: str


@dataclass(frozen=True, slots=True)
class SentinelPlan:
    """Plano filtrado e diagnósticos de paths para uma jornada selecionada."""

    module_prefix: str
    occurrences: tuple[SentinelPlanOccurrence, ...]
    invalid_paths: tuple[str, ...]

    @property
    def occurrence_count(self) -> int:
        """Conta ocorrências planejadas, incluindo paths que se repetem."""
        return len(self.occurrences)

    @property
    def can_start(self) -> bool:
        """Indica se o plano passou pelas verificações básicas de prontidão."""
        return bool(self.occurrences) and not self.invalid_paths

    @property
    def start_block_reason(self) -> str | None:
        """Explica por que o plano ainda não pode ser iniciado."""
        if self.invalid_paths:
            return "paths inválidos"
        if not self.occurrences:
            return "plano vazio"
        return None


class SentinelPlanService:
    """Lê a ordem lógica e aplica a disponibilidade canônica do catálogo."""

    def __init__(
        self,
        catalog_service: CatalogService | None = None,
        order_path: Path = ORDEM_PATH,
    ) -> None:
        self._catalog_service = catalog_service or CatalogService()
        self._order_path = order_path
        self._reader: ModuleType | None = None
        self._reader_stamp: tuple[int, int] | None = None
        self._blocks: list | None = None
        self._blocks_stamp: tuple[int, int] | None = None

    def load_modules_for_client(
        self, client_key: str, client_version: int | None
    ) -> tuple[SentinelModule, ...]:
        """Retorna prefixos com ocorrências disponíveis, na ordem do YAML.

        Prefixos pais agregam as ocorrências dos blocos descendentes, seguindo
        a semântica de seleção de ``--modulo``. Blocos explícitos também entram.
        """
        available_paths = {
            item.path
            for item in self._catalog_service.load_items_for_client(
                client_key, client_version
            )
        }
        reader, blocks = self._read_order()

        block_counts: list[tuple[str, int, bool]] = []
        for block in blocks:
            count = sum(path in available_paths for path in block.ordem)
            if count:
                block_counts.append((block.modulo, count, block.somente_explicito))

        totals: dict[str, int] = {}
        explicit: dict[str, bool] = {}
        ordered_prefixes: list[str] = []
        for block_path, count, explicit_only in block_counts:
            parts = block_path.split("/")
            for end in range(1, len(parts) + 1):
                prefix = "/".join(parts[:end])
                if prefix not in totals:
                    totals[prefix] = 0
                    explicit[prefix] = False
                    ordered_prefixes.append(prefix)
                totals[prefix] += count
            explicit[block_path] = explicit[block_path] or explicit_only

        return tuple(
            SentinelModule(
                path=prefix,
                parent_path=prefix.rpartition("/")[0] or None,
                explicit_only=explicit[prefix],
                occurrence_count=totals[prefix],
            )
            for prefix in ordered_prefixes
        )

    def build_plan(
        self, client_key: str, client_version: int | None, module_prefix: str
    ) -> SentinelPlan:
        """Monta a sequência como a CLI, filtrada por prefixo e cliente."""
        if not module_prefix:
            raise ValueError("module_prefix deve ser informado para montar o plano.")

        available_paths = {
            item.path
            for item in self._catalog_service.load_items_for_client(
                client_key, client_version
            )
        }
        reader, blocks = self._read_order()
        scoped_entries = reader.filtrar_por_modulo(
            reader.entradas_globais(blocks), module_prefix
        )
        occurrences = tuple(
            SentinelPlanOccurrence(
                index=index,
                path=path,
            )
            for index, (_module, path, _global_occurrence) in enumerate(
                (entry for entry in scoped_entries if entry[1] in available_paths),
                start=1,
            )
        )
        invalid_paths = tuple(
            dict.fromkeys(
                path
                for _module, path, _global_occurrence in scoped_entries
                if path in available_paths and not (PROJECT_ROOT / path).is_file()
            )
        )
        return SentinelPlan(module_prefix, occurrences, invalid_paths)

    @staticmethod
    def _file_stamp(path: Path) -> tuple[int, int]:
        stat = path.stat()
        return stat.st_mtime_ns, stat.st_size

    def _read_order(self) -> tuple[ModuleType, list]:
        """Reusa leitor e blocos enquanto ``ordem_reader.py``/``ordem.yaml`` não mudarem."""
        reader_stamp = self._file_stamp(SENTINELA_DIR / "ordem_reader.py")
        if self._reader is None or reader_stamp != self._reader_stamp:
            self._reader = self._load_order_reader()
            self._reader_stamp = reader_stamp
            self._blocks = None
        blocks_stamp = self._file_stamp(self._order_path)
        if self._blocks is None or blocks_stamp != self._blocks_stamp:
            self._blocks = self._reader.ler_modulos(self._order_path)
            self._blocks_stamp = blocks_stamp
        return self._reader, self._blocks

    def _load_order_reader(self) -> ModuleType:
        """Carrega o leitor da Sentinela sem colisão com imports da aplicação."""
        reader_path = SENTINELA_DIR / "ordem_reader.py"
        if not reader_path.is_file():
            raise FileNotFoundError(f"Leitor da ordem não encontrado: {reader_path}")
        spec = importlib.util.spec_from_file_location(
            "_gui_v2_sentinela_ordem_reader", reader_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Não foi possível carregar o leitor: {reader_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(spec.name, None)
            raise
        return module
