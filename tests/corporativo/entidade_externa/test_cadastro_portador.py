from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.entidade_externa.cadastro_portador.navegar_para_portador_flow import (
    acessar_portador,
)
from flows.corporativo.entidade_externa.cadastro_portador.preencher_dados_gerais_portador_flow import (
    preencher_dados_gerais_portador,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_portador(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Portador.")

    dados_cliente = contexto_cliente.dados_cliente()
    portador = contexto_cliente.portador_cr()

    login(page, dados_cliente)
    acessar_portador(page)
    preencher_dados_gerais_portador(page, portador)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Portador.")
