import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.solicitacao_materiais.consultar_solicitacao_materiais.consultar_solicitacao_materiais_flow import (
    consultar_solicitacao_materiais,
)
from flows.almoxarifado.movimentacao_interna.solicitacao_materiais.consultar_solicitacao_materiais.selecionar_solicitacao_flow import (
    selecionar_solicitacao,
)
from flows.almoxarifado.movimentacao_interna.solicitacao_materiais.navegar_para_solicitacao_materiais_flow import (
    acessar_solicitacao_materiais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_solicitacao_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Solicitação de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()
    ur = contexto_cliente.ur_padrao()
    material = contexto_cliente.material_padrao()
    
    login(page, dados_cliente)
    acessar_solicitacao_materiais(page)
    consultar_solicitacao_materiais(page,almoxarifado, ur, material)

    if not selecionar_solicitacao(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Solicitação de Materiais.")
