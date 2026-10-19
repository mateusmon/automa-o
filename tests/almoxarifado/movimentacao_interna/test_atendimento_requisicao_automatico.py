import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.navegar_para_atendimento_requisicao_flow import (
    acessar_atendimento_requisicao,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.selecionar_almoxarifado_flow import (
    selecionar_almoxarifado,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.selecionar_requisicao_automatico_flow import (
    selecionar_requisicao_automatico,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_atendimento_requisicao_automatico(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Atendimento Automático de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_atendimento_requisicao(page)
    selecionar_almoxarifado(page, almoxarifado)    

    if not selecionar_requisicao_automatico(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Atendimento Automático de Requisição.")
