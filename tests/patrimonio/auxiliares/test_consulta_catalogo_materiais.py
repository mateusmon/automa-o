import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.catalogo_materiais.consultar_catalogo_flow import (
    consultar_catalogo,
)
from flows.patrimonio.auxiliares.catalogo_materiais.navegar_para_catalogo_materiais_flow import (
    acessar_catalogo_materiais,
)
from flows.patrimonio.auxiliares.catalogo_materiais.selecionar_catalogo_flow import (
    selecionar_catalogo,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_catalogo_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Catálogo de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_catalogo_materiais(page)
    consultar_catalogo(page, ug)

    if not selecionar_catalogo(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Catálogo de Materiais.")
