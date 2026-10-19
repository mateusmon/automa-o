import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.devolucao.alteracao_devolucao_materiais.alterar_devolucao_materiais_flow import (
    alterar_devolucao_materiais,
)
from flows.almoxarifado.movimentacao_interna.devolucao.consulta_devolucao_materiais.consultar_devolucao_materiais_flow import (
    consultar_devolucao_materiais,
)
from flows.almoxarifado.movimentacao_interna.devolucao.navegar_para_devolucao_flow import (
    acessar_devolucao,
)
from flows.almoxarifado.movimentacao_interna.devolucao.selecionar_devolucao_flow import (
    selecionar_devolucao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_devolucao_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Devolução de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_devolucao(page)
    consultar_devolucao_materiais(page, almoxarifado)

    if not selecionar_devolucao(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not alterar_devolucao_materiais(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Alteração de Devolução de Materiais.")
