import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.calendario_requisicao.navegar_para_calendario_requisicao_flow import (
    acessar_calendario_requisicao,
)
from flows.almoxarifado.auxiliares.calendario_requisicao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.auxiliares.calendario_requisicao.verificar_calendario_flow import (
    verificar_calendario,
)
from flows.shared.confirmar_movimentacao_flow import confirmar_movimentacao
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_calendario_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Calendário de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_calendario_requisicao(page)

    if verificar_calendario(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    preencher_dados_gerais(page)
    confirmar_movimentacao(page)
    page.wait_for_timeout(2_000)
    logout(page)

    logger.success("Finalizou teste de Calendário de Requisição.")
