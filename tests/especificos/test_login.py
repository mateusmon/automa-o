from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_login(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Login.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    logout(page)
    
    logger.success("Finalizou teste de Login.")