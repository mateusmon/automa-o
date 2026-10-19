"""Representação independente de interface de um teste do catálogo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestItem:
    """Um teste disponível para exibição e seleção na GUI.

    ``path`` identifica o arquivo no catálogo canônico. Quando a seleção for
    refinada até uma função ou parametrização, ``nodeid`` guarda o alvo exato
    do Pytest e passa a ser a identidade da seleção.
    """

    name: str
    path: str
    module: str
    section: str
    nodeid: str | None = None
    description: str | None = None
    visible: bool = True

    @property
    def selection_id(self) -> str:
        """Retorna a chave estável da seleção, priorizando o nodeid do Pytest."""
        return self.nodeid or self.path

    @property
    def pytest_target(self) -> str:
        """Retorna o alvo que uma futura execução deverá entregar ao Pytest."""
        return self.nodeid or self.path
