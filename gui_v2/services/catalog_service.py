"""Leitura do catálogo canônico pela nova interface, sem alterá-lo."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
import importlib
from pathlib import Path
import sys

from gui_v2.models.test_item import TestItem


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEGACY_GUI_DIR = PROJECT_ROOT / "gui"


@contextmanager
def _legacy_catalog_import_path(gui_dir: Path) -> Iterator[None]:
    """Expõe temporariamente o contrato de importação do catálogo legado."""
    directory = str(gui_dir)
    inserted = directory not in sys.path
    if inserted:
        sys.path.insert(0, directory)
    try:
        yield
    finally:
        if inserted:
            sys.path.remove(directory)


class CatalogService:
    """Converte, em ordem, o catálogo legado somente de leitura em ``TestItem``."""

    def __init__(self, legacy_gui_dir: Path = LEGACY_GUI_DIR) -> None:
        self._legacy_gui_dir = legacy_gui_dir

    def load_items(self) -> tuple[TestItem, ...]:
        """Carrega todos os itens do catálogo, sem filtro de cliente ou versão."""
        return self._items_from_modules(self._load_modules())

    def load_items_for_client(
        self, client_key: str, client_version: int | None
    ) -> tuple[TestItem, ...]:
        """Carrega somente os itens visíveis para o cliente e versão informados."""
        if not client_key:
            raise ValueError("client_key deve ser informado para filtrar o catálogo.")
        filter_modules = self._load_filter()
        filtered_modules = filter_modules(
            self._load_modules(), client_key, client_version
        )
        return self._items_from_modules(filtered_modules)

    def _items_from_modules(
        self, modules: Mapping[str, Mapping[str, object]]
    ) -> tuple[TestItem, ...]:
        """Converte o mapeamento já ordenado do catálogo em itens da GUI."""
        return tuple(
            self._to_test_item(module_name, section_name, entry)
            for module_name, module_data in modules.items()
            for section_name, entries in module_data.get("sections", {}).items()
            for entry in entries
        )

    def _load_modules(self) -> Mapping[str, Mapping[str, object]]:
        if not self._legacy_gui_dir.is_dir():
            raise FileNotFoundError(f"Diretório da GUI legada não encontrado: {self._legacy_gui_dir}")
        with _legacy_catalog_import_path(self._legacy_gui_dir):
            module = importlib.import_module("catalog.modules_catalog")
        modules = getattr(module, "MODULES", None)
        if not isinstance(modules, Mapping):
            raise TypeError("O catálogo legado deve expor MODULES como um mapeamento.")
        return modules

    def _load_filter(
        self,
    ) -> Callable[[Mapping[str, Mapping[str, object]], str, int | None], dict]:
        """Obtém a regra canônica de visibilidade, sem reimplementá-la."""
        with _legacy_catalog_import_path(self._legacy_gui_dir):
            module = importlib.import_module("core.module_filter")
        filter_modules = getattr(module, "filtrar_modulos_por_cliente", None)
        if not callable(filter_modules):
            raise TypeError("O filtro legado não expõe filtrar_modulos_por_cliente.")
        return filter_modules

    @staticmethod
    def _to_test_item(module: str, section: str, entry: object) -> TestItem:
        if not isinstance(entry, Mapping):
            raise TypeError(f"Item inválido no catálogo: {entry!r}")
        name = entry.get("name")
        path = entry.get("path")
        if not isinstance(name, str) or not name:
            raise ValueError(f"Item sem nome no catálogo: {entry!r}")
        if not isinstance(path, str) or not path:
            raise ValueError(f"Item sem path no catálogo: {entry!r}")
        description = entry.get("description")
        if description is not None and not isinstance(description, str):
            raise TypeError(f"Descrição inválida no catálogo: {entry!r}")
        return TestItem(
            name=name,
            path=path,
            module=module,
            section=section,
            description=description,
        )
