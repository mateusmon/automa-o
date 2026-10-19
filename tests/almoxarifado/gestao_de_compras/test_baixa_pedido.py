import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.baixa_pedido.baixar_pedido_flow import (
    baixar_pedido,
)
from flows.almoxarifado.gestao_de_compras.baixa_pedido.consultar_pedido_flow import (
    consultar_pedido,
)
from flows.almoxarifado.gestao_de_compras.baixa_pedido.navegar_para_baixa_flow import (
    acessar_baixa_pedido,
)
from flows.almoxarifado.gestao_de_compras.baixa_pedido.selecionar_pedido_flow import (
    selecionar_pedido,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_baixa_pedido(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Baixa de Pedido.")

    dados_cliente = contexto_cliente.dados_cliente()
    ua_data = contexto_cliente.ua()

    login(page, dados_cliente)
    acessar_baixa_pedido(page)
    consultar_pedido(page, ua_data)

    if not selecionar_pedido(page, ua_data):
        logger.warning("Pulando teste.")
        pytest.skip()

    baixar_pedido(page)
    logout(page)

    logger.success("Finalizou teste de Baixa de Pedido.")
