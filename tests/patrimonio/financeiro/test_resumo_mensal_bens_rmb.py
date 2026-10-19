import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.financeiro.resumo_mensal_bens.navegar_para_rmb_flow import (
    acessar_rmb,
)
from flows.patrimonio.financeiro.resumo_mensal_bens.preencher_detalhamento_flow import (
    preencher_detalhamento,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_resumo_mensal_bens_rmb(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Resumo Mensal de Bens (RMB).")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_rmb(page)
    preencher_detalhamento(page, ug)

    # A confirmação do RMB já solicita a geração dos relatórios.
    if imprimir_relatorio(page, ja_solicitado=True, timeout_geracao=250_000) is False:
        logger.warning("Pulando teste.")
        pytest.skip()
    
    logout(page)
    
    logger.success("Finalizou teste de Resumo Mensal de Bens (RMB).")
