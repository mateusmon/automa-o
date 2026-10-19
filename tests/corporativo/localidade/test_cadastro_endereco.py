from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_endereco.navegar_para_endereco_flow import (
    acessar_endereco,
)
from flows.corporativo.localidade.cadastro_endereco.preencher_dados_gerais_endereco_flow import (
    preencher_dados_gerais_endereco,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_endereco(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Endereço.")

    dados_cliente = contexto_cliente.dados_cliente()
    endereco = contexto_cliente.endereco_cr()

    login(page, dados_cliente)
    acessar_endereco(page)
    preencher_dados_gerais_endereco(page, endereco)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Endereço.")
