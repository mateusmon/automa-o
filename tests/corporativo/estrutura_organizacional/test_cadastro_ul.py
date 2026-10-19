from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ul.navegar_para_ul_flow import (
    acessar_ul,
)
from flows.corporativo.estrutura_organizacional.cadastro_ul.preencher_dados_gerais_ul_flow import (
    preencher_dados_gerais_ul,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_ul(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de UL - Unidade de Localização.")

    dados_cliente = contexto_cliente.dados_cliente()
    ul = contexto_cliente.unidade_localizacao_cr()

    login(page, dados_cliente)
    acessar_ul(page)
    preencher_dados_gerais_ul(page, ul)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de UL - Unidade de Localização.")
