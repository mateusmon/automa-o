import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.navegar_para_recebimento_devolucao_flow import (
    acessar_recebimento_devolucao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.receber_devolucao_flow import (
    efetuar_recebimento_devolucao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.selecionar_almoxarifado_flow import (
    selecionar_almoxarifado,
)
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.selecionar_devolucao_a_receber_flow import (
    selecionar_devolucao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.selecionar_ug_flow import (
    selecionar_ug,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_recebimento_devolucao_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Recebimento de Devolução.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_recebimento_devolucao(page)
    selecionar_ug(page, ug)
    selecionar_almoxarifado(page, almoxarifado)

    if not selecionar_devolucao(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    efetuar_recebimento_devolucao(page, almoxarifado)
    logout(page)
    
    logger.success("Finalizou teste de Recebimento de Devolução.")
