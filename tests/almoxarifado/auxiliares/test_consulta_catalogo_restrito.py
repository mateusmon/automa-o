import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.catalogo_restrito.consulta_catalogo_restrito.consultar_catalogo_restrito_flow import (
    consultar_catalogo_restrito,
)
from flows.almoxarifado.auxiliares.catalogo_restrito.navegar_para_catalogo_restrito_flow import (
    acessar_catalogo_restrito,
)
from flows.almoxarifado.auxiliares.catalogo_restrito.selecionar_catalogo_restrito_flow import (
    selecionar_catalogo_restrito,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_catalogo_restrito(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Catálogo Restrito.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_catalogo_restrito(page)
    consultar_catalogo_restrito(page, almoxarifado)
    
    if not selecionar_catalogo_restrito(page, "CATÁLOGO DE TESTE AUTOMATIZADO"):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Catálogo Restrito.")
