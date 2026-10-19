from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ur.navegar_para_ur_flow import (
    acessar_ur,
)
from flows.corporativo.estrutura_organizacional.cadastro_ur.preencher_dados_gerais_ur_flow import (
    preencher_dados_gerais_ur,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_ur(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de UR - Unidade de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.unidade_requisicao_cr()

    login(page, dados_cliente)
    acessar_ur(page)
    preencher_dados_gerais_ur(page, ur)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de UR - Unidade de Requisição.")
