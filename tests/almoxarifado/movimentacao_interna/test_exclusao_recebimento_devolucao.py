import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.consulta_recebimento_devolucao.consultar_recebimento_devolucao_flow import (
    consultar_recebimento_devolucao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.navegar_para_recebimento_devolucao_flow import (
    acessar_recebimento_devolucao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_devolucao.selecionar_devolucao_flow import (
    selecionar_devolucao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_recebimento_devolucao_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Recebimento de Devolução.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_recebimento_devolucao(page)
    consultar_recebimento_devolucao(page, almoxarifado, ug)

    if not selecionar_devolucao(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Recebimento de Devolução.")
