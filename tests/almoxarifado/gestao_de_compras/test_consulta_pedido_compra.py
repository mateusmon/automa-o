import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.pedido_de_compra.consulta_pedido_de_compra.consultar_pedido_compra_flow import (
    consultar_pedido_compra,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_compra.navegar_para_pedido_compra_flow import (
    acessar_pedido_compra,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_pedido_compra(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Pedido de Compra.")

    dados_cliente = contexto_cliente.dados_cliente()
    ua = contexto_cliente.ua()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_pedido_compra(page)

    if not consultar_pedido_compra(page, ua, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Pedido de Compra.")
