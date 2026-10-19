import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.inventario.consulta_inventario.consultar_inventario_flow import (
    consultar_inventario,
)
from flows.almoxarifado.gestao_de_estoque.inventario.consulta_inventario.selecionar_inventario_flow import (
    selecionar_inventario,
)
from flows.almoxarifado.gestao_de_estoque.inventario.navegar_para_pagina_inventario_flow import (
    acessar_inventario,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_inventario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Inventário.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_inventario(page)
    consultar_inventario(page, almoxarifado)

    if not selecionar_inventario(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Inventário.")
