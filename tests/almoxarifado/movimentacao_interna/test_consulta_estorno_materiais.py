import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.estorno.consulta_estorno_materiais.consultar_estorno_materiais_flow import (
    consultar_estorno_materiais,
)
from flows.almoxarifado.movimentacao_interna.estorno.navegar_para_estorno_flow import (
    acessar_estorno,
)
from flows.almoxarifado.movimentacao_interna.estorno.selecionar_estorno_flow import (
    selecionar_estorno,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_estorno_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Estorno de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    funcionario = contexto_cliente.funcionario_padrao()

    login(page, dados_cliente)
    acessar_estorno(page)
    consultar_estorno_materiais(page, funcionario)

    if not selecionar_estorno(page, funcionario):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Estorno de Materiais.")
