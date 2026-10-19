import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.evento.navegar_para_evento_flow import (
    acessar_evento,
)
from flows.almoxarifado.gestao_de_compras.evento.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_evento(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Evento.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_evento(page):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    preencher_dados_gerais(page)
    logout(page)

    logger.success("Finalizou teste de Cadastro de Evento.")
