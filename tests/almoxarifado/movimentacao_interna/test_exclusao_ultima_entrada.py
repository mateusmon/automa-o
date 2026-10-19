import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.entrada_materiais.consultar_ultima_entrada_flow import (
    consultar_ultima_entrada,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.navegar_para_entrada_materiais_flow import (
    acessar_entrada_materiais,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_excluir_ultima_entrada(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Entrada.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_entrada_materiais(page)

    if not consultar_ultima_entrada(page, almoxarifado, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Entrada.")
