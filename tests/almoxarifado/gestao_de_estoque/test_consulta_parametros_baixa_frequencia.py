import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.parametros_baixa_frequencia.consulta_parametros.consultar_parametros_flow import (
    consultar_parametros,
)
from flows.almoxarifado.gestao_de_estoque.parametros_baixa_frequencia.consulta_parametros.selecionar_parametros_flow import (
    selecionar_parametros,
)
from flows.almoxarifado.gestao_de_estoque.parametros_baixa_frequencia.navegar_para_baixa_frequencia_flow import (
    acessar_parametro_baixa_frequencia,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_parametros_baixa_frequencia(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de consulta de Parâmetros de Baixa Frequência.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)

    if not acessar_parametro_baixa_frequencia(page):
        logger.warning("O submódulo 'Parâmetros de Baixa Frequência' não está disponível para este cliente.")
        pytest.skip()
        
    consultar_parametros(page, almoxarifado)

    if not selecionar_parametros(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Parâmetros de Baixa Frequência.")
