from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcao.navegar_para_funcao_flow import (
    acessar_funcao,
)
from flows.corporativo.funcionario.cadastro_funcao.preencher_dados_gerais_funcao_flow import (
    preencher_dados_gerais_funcao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_funcao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Função.")

    dados_cliente = contexto_cliente.dados_cliente()
    funcao = contexto_cliente.funcao_cr()

    login(page, dados_cliente)
    acessar_funcao(page)
    preencher_dados_gerais_funcao(page, funcao)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Função.")
