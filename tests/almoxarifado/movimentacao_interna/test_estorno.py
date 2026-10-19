import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.estorno.consultar_movimento_flow import (
    consultar_movimento,
)
from flows.almoxarifado.movimentacao_interna.estorno.escolher_material_flow import (
    escolher_material,
)
from flows.almoxarifado.movimentacao_interna.estorno.navegar_para_estorno_flow import (
    acessar_estorno,
)
from flows.almoxarifado.movimentacao_interna.estorno.selecionar_movimento_flow import (
    selecionar_movimento,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_estorno(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Estorno de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_estorno(page)
    consultar_movimento(page, almoxarifado)

    if not selecionar_movimento(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    escolher_material(page, material)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Estorno de Materiais.")
