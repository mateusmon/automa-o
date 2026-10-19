import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.calendario_requisicao.excluir_dias_requisicao_flow import (
    excluir_dias_requisicao,
)
from flows.almoxarifado.auxiliares.calendario_requisicao.navegar_para_calendario_requisicao_flow import (
    acessar_calendario_requisicao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_calendario_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Calendário de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_calendario_requisicao(page)
    excluir_dias_requisicao(page, ur)
    logout(page)

    logger.success("Finalizou teste de Exclusão de Calendário de Requisição.")
