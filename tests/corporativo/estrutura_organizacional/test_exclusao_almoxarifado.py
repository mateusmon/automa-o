import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.consultar_almoxarifado_flow import (
    consultar_almoxarifado,
)
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.navegar_para_almoxarifado_flow import (
    acessar_almoxarifado,
)
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.selecionar_almoxarifado_flow import (
    selecionar_almoxarifado,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_almoxarifado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Almoxarifado.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_cr()

    login(page, dados_cliente)
    acessar_almoxarifado(page)
    consultar_almoxarifado(page, almoxarifado)

    if not selecionar_almoxarifado(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Almoxarifado.")
