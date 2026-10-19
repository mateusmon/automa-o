import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.parametros_alta_frequencia.consultar_parametros_flow import (
    consultar_parametros,
)
from flows.almoxarifado.gestao_de_estoque.parametros_alta_frequencia.navegar_para_alta_frequencia_flow import (
    acessar_parametro_alta_frequencia,
)
from flows.almoxarifado.gestao_de_estoque.parametros_alta_frequencia.selecionar_resultado_flow import (
    selecionar_resultado,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_parametros_alta_frequencia(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Parâmetros de Alta Frequência.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)

    if not acessar_parametro_alta_frequencia(page):
        logger.info("O submódulo 'Parâmetros de Alta Frequência' não está disponível para este cliente.")
        pytest.skip()

    consultar_parametros(page, almoxarifado)

    if not selecionar_resultado(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Parâmetros de Alta Frequência.")
