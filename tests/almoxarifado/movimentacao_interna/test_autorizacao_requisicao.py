import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.autorizacao_requisicao.autorizar_requisicao_flow import (
    autorizar_requisicao,
)
from flows.almoxarifado.movimentacao_interna.autorizacao_requisicao.consultar_requisicao_flow import (
    consultar_requisicao,
)
from flows.almoxarifado.movimentacao_interna.autorizacao_requisicao.navegar_para_autorizacao_requisicao_flow import (
    acessar_autorizacao_requisicao,
)
from flows.almoxarifado.movimentacao_interna.autorizacao_requisicao.selecionar_requisicao_flow import (
    selecionar_requisicao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_autorizacao_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Autorização de Requisição.")
    
    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_autorizacao_requisicao(page)
    consultar_requisicao(page)

    if not selecionar_requisicao(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()

    autorizar_requisicao(page)
    logout(page)
    
    logger.success("Finalizou teste de Autorização de Requisição.")
