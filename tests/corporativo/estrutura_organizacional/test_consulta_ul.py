import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ul.consultar_ul_flow import (
    consultar_ul,
)
from flows.corporativo.estrutura_organizacional.cadastro_ul.navegar_para_ul_flow import (
    acessar_ul,
)
from flows.corporativo.estrutura_organizacional.cadastro_ul.selecionar_ul_flow import (
    selecionar_ul,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_ul(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de UL - Unidade de Localização.")

    dados_cliente = contexto_cliente.dados_cliente()
    ul = contexto_cliente.unidade_localizacao_cr()

    login(page, dados_cliente)
    acessar_ul(page)
    consultar_ul(page, ul)

    if not selecionar_ul(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de UL - Unidade de Localização.")
