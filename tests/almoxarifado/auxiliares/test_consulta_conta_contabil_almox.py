# Não é possível criar uma conta contábil aqui, apenas consultar

from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.conta.consultar_conta_flow import consultar_conta
from flows.almoxarifado.auxiliares.conta.navegar_para_conta_flow import (
    acessar_conta_contabil,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_conta_contabil(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Conta Contábil.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_conta_contabil(page)
    consultar_conta(page)
    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Conta Contábil.")
