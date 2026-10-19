from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_cc.navegar_para_cc_flow import (
    acessar_cc,
)
from flows.corporativo.estrutura_organizacional.cadastro_cc.preencher_dados_gerais_cc_flow import (
    preencher_dados_gerais_cc,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_cc(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de CC - Centro de Custos.")

    dados_cliente = contexto_cliente.dados_cliente()
    cc = contexto_cliente.centro_custo_cr()

    login(page, dados_cliente)
    acessar_cc(page)
    preencher_dados_gerais_cc(page, cc)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de CC - Centro de Custos.")
