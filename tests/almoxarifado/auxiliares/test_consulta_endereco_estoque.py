import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.endereco_estoque.consultar_endereco_flow import (
    consultar_endereco,
)
from flows.almoxarifado.auxiliares.endereco_estoque.navegar_para_endereco_estoque_flow import (
    acessar_endereco_estoque,
)
from flows.almoxarifado.auxiliares.endereco_estoque.selecionar_endereco_flow import (
    selecionar_endereco,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_endereco_estoque(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Endereço de Estoque.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    endereco = "ATMTZD"

    login(page, dados_cliente)
    acessar_endereco_estoque(page)
    consultar_endereco(page, almoxarifado, endereco)

    if not selecionar_endereco(page, endereco):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Endereço de Estoque.")
