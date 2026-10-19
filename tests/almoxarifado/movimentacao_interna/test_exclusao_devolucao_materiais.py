import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.devolucao.consulta_devolucao_materiais.consultar_devolucao_materiais_flow import (
    consultar_devolucao_materiais,
)
from flows.almoxarifado.movimentacao_interna.devolucao.navegar_para_devolucao_flow import (
    acessar_devolucao,
)
from flows.almoxarifado.movimentacao_interna.devolucao.selecionar_devolucao_flow import (
    selecionar_devolucao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_devolucao_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Devolução de Material.")
    
    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_devolucao(page)
    consultar_devolucao_materiais(page, almoxarifado)

    if not selecionar_devolucao(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()
        
    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Devolução de Material.")
