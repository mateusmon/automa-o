import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.devolucao.navegar_para_devolucao_flow import (
    acessar_devolucao,
)
from flows.almoxarifado.movimentacao_interna.devolucao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.movimentacao_interna.devolucao.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.almoxarifado.movimentacao_interna.devolucao.preencher_itens_flow import (
    preencher_itens,
)
from flows.almoxarifado.movimentacao_interna.devolucao.selecionar_requisicao_flow import (
    selecionar_requisicao_devolucao,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_devolucao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Devolução de Material de Requisição.")
    
    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ur = contexto_cliente.ur_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_devolucao(page)
    preencher_dados_gerais(page, almoxarifado, ur)
    
    if not selecionar_requisicao_devolucao(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_documentos(page)
    
    if preencher_itens(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Devolução de Material de Requisição.")
