
import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.navegar_para_cadastro_requisicao_flow import (
    acessar_cadastro_requisicao,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.consultar_cadastro_requisicao.consultar_requisicao_flow import (
    consultar_requisicao,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.selecionar_requisicao_flow import (
    selecionar_requisicao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_excluir_solicitacao_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Cadastro de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_cadastro_requisicao(page)
    consultar_requisicao(page, almoxarifado, ur, material)

    if not selecionar_requisicao(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Cadastro de Requisição.")
