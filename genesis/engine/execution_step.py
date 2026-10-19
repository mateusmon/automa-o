"""Execução instrumentada das etapas das rotinas do Genesis."""

from collections.abc import Callable

from engine.execution_context import ExecutionContext
from utils import trace


Etapa = Callable[[ExecutionContext], None]


def executar_etapa(
    context: ExecutionContext,
    etapa: Etapa,
    nome: str | None = None,
) -> None:
    """Executa uma etapa com um trace isolado, salvo somente em caso de falha."""
    nome_trace = nome or etapa.__name__
    trace.executar_com_trace(
        context.browser_manager.context,
        nome_trace,
        lambda: etapa(context),
    )
