import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.parametros_baixa_frequencia.navegar_para_baixa_frequencia_flow import (
    acessar_parametro_baixa_frequencia,
)
from flows.almoxarifado.gestao_de_estoque.parametros_baixa_frequencia.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_parametros_baixa_frequencia(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Parâmetros de Baixa Frequência.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    if not acessar_parametro_baixa_frequencia(page):
        logger.warning("O submódulo 'Parâmetros de Baixa Frequência' não está disponível para este cliente.")
        pytest.skip()

    if not preencher_dados_gerais(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Parâmetros de Baixa Frequência.")
