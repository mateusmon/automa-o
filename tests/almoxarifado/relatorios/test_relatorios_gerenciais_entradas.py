import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.relatorios.rel_gerenciais_entradas.navegar_para_rel_gerenciais_entradas_flow import (
    acessar_rel_gerenciais_entradas,
)
from flows.almoxarifado.relatorios.rel_gerenciais_entradas.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_gerenciais_entrada(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    logger.info("Iniciou teste de Rel. Gerenciais - Entrada.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_rel_gerenciais_entradas(page)
    preencher_dados_gerais(page, ug, almoxarifado)

    if not imprimir_relatorio(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    logger.success("Finalizou teste de Rel. Gerenciais - Entrada.")
