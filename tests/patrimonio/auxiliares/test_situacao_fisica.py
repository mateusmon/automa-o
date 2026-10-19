import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.situacao_fisica.navegar_para_situacao_fisica_flow import (
    acessar_situacao_fisica,
)
from flows.patrimonio.auxiliares.situacao_fisica.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_situacao_fisica(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Situação Física.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_situacao_fisica(page):
        logger.warning("Pulando teste.")
        pytest.skip()
        
    preencher_dados_gerais(page, "METAFÍSICO")
    logout(page)
    
    logger.success("Finalizou teste de Situação Física.")
