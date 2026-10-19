import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_cidade.consultar_cidade_flow import (
    consultar_cidade,
)
from flows.corporativo.localidade.cadastro_cidade.navegar_para_cidade_flow import (
    acessar_cidade,
)
from flows.corporativo.localidade.cadastro_cidade.selecionar_cidade_flow import (
    selecionar_cidade,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_cidade(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Cidade.")

    dados_cliente = contexto_cliente.dados_cliente()
    cidade = contexto_cliente.cidade_cr()

    login(page, dados_cliente)
    acessar_cidade(page)
    consultar_cidade(page, cidade)

    if not selecionar_cidade(page, cidade):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Cidade.")
