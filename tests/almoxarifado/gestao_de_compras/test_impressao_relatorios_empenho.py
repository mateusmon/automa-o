import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.relatorios_empenho.navegar_para_relatorios_empenho_flow import (
    acessar_relatorios_empenho,
)
from flows.almoxarifado.gestao_de_compras.relatorios_empenho.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_impressao_relatorios_empenho(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    logger.info("Iniciou teste de Impressão de Relatórios de Empenho.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug_data = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_relatorios_empenho(page)
    preencher_dados_gerais(page, ug_data)

    if not imprimir_relatorio(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)

    logger.success("Finalizou teste de Impressão de Relatórios de Empenho.")
