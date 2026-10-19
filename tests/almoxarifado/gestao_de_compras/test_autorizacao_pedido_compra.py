import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.autorizacao_pedido_compra.autorizar_pedido_flow import (
    autorizar_pedido,
)
from flows.almoxarifado.gestao_de_compras.autorizacao_pedido_compra.navegar_para_autorizacao_pedido_flow import (
    acessar_autorizacao_pedido_compra,
)
from flows.almoxarifado.gestao_de_compras.autorizacao_pedido_compra.selecionar_ug_flow import (
    selecionar_ug,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_autorizacao_pedido_compra(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Autorização de Pedido de Compra.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug_data = contexto_cliente.ug()
    
    login(page, dados_cliente)

    if not acessar_autorizacao_pedido_compra(page):
        logger.warning("Pulando teste.")
        pytest.skip()
        
    selecionar_ug(page, ug_data)

    if not autorizar_pedido(page):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    logout(page)

    logger.success("Finalizou teste de Autorização de Pedido de Compra.")
