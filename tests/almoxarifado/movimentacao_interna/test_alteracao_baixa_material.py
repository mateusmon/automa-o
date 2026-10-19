import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.baixa.alteracao_baixa_material.alterar_quantidade_flow import (
    alterar_quantidade,
)
from flows.almoxarifado.movimentacao_interna.baixa.consulta_baixa_material.consultar_baixa_material_flow import (
    consultar_baixa_material,
)
from flows.almoxarifado.movimentacao_interna.baixa.navegar_para_baixa_flow import (
    acessar_baixa,
)
from flows.almoxarifado.movimentacao_interna.baixa.selecionar_baixa_flow import (
    selecionar_baixa,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alterar_baixa_material(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Baixa de Material.")
    
    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_baixa(page)
    consultar_baixa_material(page, almoxarifado, material)

    if not selecionar_baixa(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_quantidade(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Baixa de Material.")
