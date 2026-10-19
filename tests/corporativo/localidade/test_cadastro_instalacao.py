from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_instalacao.navegar_para_instalacao_flow import (
    acessar_instalacao,
)
from flows.corporativo.localidade.cadastro_instalacao.preencher_dados_gerais_instalacao_flow import (
    preencher_dados_gerais_instalacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_instalacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Instalação.")

    dados_cliente = contexto_cliente.dados_cliente()
    instalacao = contexto_cliente.instalacao_cr()

    login(page, dados_cliente)
    acessar_instalacao(page)
    preencher_dados_gerais_instalacao(page, instalacao)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Instalação.")
