import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.consulta_atendimento_requisicao.consultar_atendimento_requisicao_flow import (
    consultar_atendimento_requisicao,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.navegar_para_atendimento_requisicao_flow import (
    acessar_atendimento_requisicao,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.selecionar_requisicao_atendida_flow import (
    selecionar_requisicao_atendida,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_atendimento_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Atendimento de Requisição.")
    
    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_atendimento_requisicao(page)
    consultar_atendimento_requisicao(page, almoxarifado, ur)

    if not selecionar_requisicao_atendida(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()
        
    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Atendimento de Requisição.")
