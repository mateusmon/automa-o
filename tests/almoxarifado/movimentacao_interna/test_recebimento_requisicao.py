import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.navegar_para_recebimento_requisicao_flow import (
    acessar_recebimento_requisicao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.receber_requisicao_flow import (
    efetuar_recebimento_requisicao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_recebimento_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Recebimento de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.ur_padrao()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_recebimento_requisicao(page)

    if not efetuar_recebimento_requisicao(page, almoxarifado, ur):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Recebimento de Requisição.")
