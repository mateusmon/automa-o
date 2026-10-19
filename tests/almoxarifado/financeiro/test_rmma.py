import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.financeiro.rmma.navegar_para_rmma_flow import acessar_rmma
from flows.almoxarifado.financeiro.rmma.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.financeiro.rmma.selecionar_item_flow import selecionar_item
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_rmma(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Emissão de Relatório RMMA.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_rmma(page)
    preencher_dados_gerais(page, ug, almoxarifado)

    if not selecionar_item(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Emissão de Relatório RMMA.")
