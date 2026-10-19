import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.estorno_baixa_bens.consulta_estorno_baixa_bens.consultar_estorno_baixa_bens_flow import (
    consultar_estorno_baixa_bens,
)
from flows.patrimonio.movimentacao.estorno_baixa_bens.consultar_baixas_flow import (
    consultar_baixas,
)
from flows.patrimonio.movimentacao.estorno_baixa_bens.navegar_para_estorno_baixa_bens_flow import (
    acessar_estorno_baixa_bens,
)
from flows.patrimonio.movimentacao.estorno_baixa_bens.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


# Apenas baixas do mês anterior (ou mais antigas) podem ser estornadas
def test_estorno_baixa_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Estorno da Baixa de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_estorno_baixa_bens(page)

    if not consultar_baixas(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_dados_gerais(page)
    consultar_estorno_baixa_bens(page, ug)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Estorno da Baixa de Bens.")