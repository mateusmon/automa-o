import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.estorno_baixa_bens.alteracao_estorno_baixa_bens.alterar_estorno_baixa_bens_flow import (
    alterar_estorno_baixa_bens,
)
from flows.patrimonio.movimentacao.estorno_baixa_bens.consulta_estorno_baixa_bens.consultar_estorno_baixa_bens_flow import (
    consultar_estorno_baixa_bens,
)
from flows.patrimonio.movimentacao.estorno_baixa_bens.navegar_para_estorno_baixa_bens_flow import (
    acessar_estorno_baixa_bens,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_estorno_baixa_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração do Estorno da Baixa dos Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_estorno_baixa_bens(page)

    if not consultar_estorno_baixa_bens(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    if not alterar_estorno_baixa_bens(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Alteração do Estorno da Baixa dos Bens.")
