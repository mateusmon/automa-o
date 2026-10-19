from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.seguranca.cadastro_perfil.navegar_para_perfil_flow import (
    acessar_perfil,
)
from flows.corporativo.seguranca.cadastro_perfil.preencher_dados_gerais_perfil_flow import (
    preencher_dados_gerais_perfil,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_perfil(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Perfil.")

    dados_cliente = contexto_cliente.dados_cliente()
    perfil = contexto_cliente.perfil_cr()

    login(page, dados_cliente)
    acessar_perfil(page)
    preencher_dados_gerais_perfil(page, perfil)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Perfil.")
