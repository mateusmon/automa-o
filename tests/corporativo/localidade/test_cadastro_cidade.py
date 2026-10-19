import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_cidade.navegar_para_cidade_flow import (
    acessar_cidade,
)
from flows.corporativo.localidade.cadastro_cidade.preencher_dados_gerais_cidade_flow import (
    preencher_dados_gerais_cidade,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_cidade(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Cidade.")

    dados_cliente = contexto_cliente.dados_cliente()
    cidade = contexto_cliente.cidade_cr()

    login(page, dados_cliente)
    acessar_cidade(page)

    if not preencher_dados_gerais_cidade(page, cidade):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Cidade.")
