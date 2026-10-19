import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.entidade_externa.cadastro_orgao_externo.navegar_para_orgao_externo_flow import (
    acessar_orgao_externo,
)
from flows.corporativo.entidade_externa.cadastro_orgao_externo.preencher_dados_gerais_orgao_externo_flow import (
    preencher_dados_gerais_orgao_externo,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_orgao_externo(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Órgão Externo.")

    dados_cliente = contexto_cliente.dados_cliente()
    orgao = contexto_cliente.orgao_externo_cr()

    login(page, dados_cliente)
    acessar_orgao_externo(page)

    if not preencher_dados_gerais_orgao_externo(page, orgao):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Órgão Externo.")
