from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_pais.navegar_para_pais_flow import (
    acessar_pais,
)
from flows.corporativo.localidade.cadastro_pais.preencher_dados_gerais_pais_flow import (
    preencher_dados_gerais_pais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_pais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de País.")

    dados_cliente = contexto_cliente.dados_cliente()
    pais = contexto_cliente.pais_cr()

    login(page, dados_cliente)
    acessar_pais(page)
    preencher_dados_gerais_pais(page, pais)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de País.")
