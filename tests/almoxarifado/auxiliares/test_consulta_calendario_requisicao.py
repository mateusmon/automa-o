import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.calendario_requisicao.navegar_para_calendario_requisicao_flow import (
    acessar_calendario_requisicao,
)
from flows.almoxarifado.auxiliares.calendario_requisicao.verificar_calendario_flow import (
    verificar_calendario,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_calendario_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Calendário de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_calendario_requisicao(page)

    if not verificar_calendario(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Calendário de Requisição.")
