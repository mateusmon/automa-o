from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.pedido_de_compra.navegar_para_pedido_compra_flow import (
    acessar_pedido_compra,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_compra.preencher_dados_pedido_flow import (
    preencher_dados_pedido,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_compra.preencher_itens_flow import (
    preencher_itens,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_pedido_compra(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Pedido de Compra.")

    dados_cliente = contexto_cliente.dados_cliente()
    ua = contexto_cliente.ua()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_pedido_compra(page)
    preencher_dados_pedido(page, ua)
    preencher_itens(page, material)
    logout(page)

    logger.success("Finalizou teste de Cadastro de Pedido de Compra.")
