import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.consulta.navegar_para_consulta_flow import acessar_consulta
from flows.almoxarifado.consulta.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_consulta(page)

    if not preencher_dados_gerais(page, almoxarifado, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page, timeout_geracao=250_000)
    logout(page)

    logger.success("Finalizou teste de Consulta de Materiais.")
