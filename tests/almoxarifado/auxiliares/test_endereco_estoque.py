from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.endereco_estoque.navegar_para_endereco_estoque_flow import (
    acessar_endereco_estoque,
)
from flows.almoxarifado.auxiliares.endereco_estoque.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_endereco_estoque(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de criação de endereço de estoque.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    endereco = "ATMTZD"

    login(page, dados_cliente)
    acessar_endereco_estoque(page)
    preencher_dados_gerais(page, almoxarifado, endereco)
    logout(page)
    
    logger.success("Finalizou teste de criação de endereço de estoque.")
