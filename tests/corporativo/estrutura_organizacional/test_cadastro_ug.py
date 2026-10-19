from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ug.navegar_para_ug_flow import (
    acessar_ug,
)
from flows.corporativo.estrutura_organizacional.cadastro_ug.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_ug(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de UG - Unidade Gestora.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.unidade_gestora_cr()

    login(page, dados_cliente)
    acessar_ug(page)
    preencher_dados_gerais(page, ug)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de UG - Unidade Gestora.")
