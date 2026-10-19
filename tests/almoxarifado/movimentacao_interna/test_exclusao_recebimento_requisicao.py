import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.consulta_recebimento_requisicao.consultar_recebimento_requisicao_flow import (
    consultar_recebimento_requisicao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.editar_recebimento_flow import (
    editar_recebimento,
)
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.navegar_para_recebimento_requisicao_flow import (
    acessar_recebimento_requisicao,
)
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.selecionar_recebimento_flow import (
    selecionar_recebimento,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_recebimento_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Recebimento de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ur = contexto_cliente.ur_padrao()
    material = contexto_cliente.material_padrao()
    
    login(page, dados_cliente)
    acessar_recebimento_requisicao(page)
    consultar_recebimento_requisicao(page, ur, almoxarifado, material)

    if not selecionar_recebimento(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    editar_recebimento(page)
    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Recebimento de Requisição.")
