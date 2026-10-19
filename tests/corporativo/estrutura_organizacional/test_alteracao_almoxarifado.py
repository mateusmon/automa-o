import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.alterar_almoxarifado_flow import (
    alterar_almoxarifado,
)
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.consultar_almoxarifado_flow import (
    consultar_almoxarifado,
)
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.navegar_para_almoxarifado_flow import (
    acessar_almoxarifado,
)
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.selecionar_almoxarifado_flow import (
    selecionar_almoxarifado,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_almoxarifado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Almoxarifado.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_cr()

    login(page, dados_cliente)
    acessar_almoxarifado(page)
    consultar_almoxarifado(page, almoxarifado)

    if not selecionar_almoxarifado(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_almoxarifado(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Almoxarifado.")
