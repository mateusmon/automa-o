import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ua.navegar_para_ua_flow import (
    acessar_ua,
)
from flows.corporativo.estrutura_organizacional.cadastro_ua.preencher_dados_gerais_ua_flow import (
    preencher_dados_gerais_ua,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_ua(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de UA - Unidade Administrativa.")

    dados_cliente = contexto_cliente.dados_cliente()
    ua = contexto_cliente.unidade_administrativa_cr()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_ua(page)

    if not preencher_dados_gerais_ua(page, ua, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Cadastro de UA - Unidade Administrativa.")
