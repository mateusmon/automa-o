from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcionario.navegar_para_funcionario_flow import (
    acessar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.preencher_dados_gerais_funcionario_flow import (
    preencher_dados_gerais_funcionario,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_funcionario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Funcionário.")

    dados_cliente = contexto_cliente.dados_cliente()
    funcionario = contexto_cliente.funcionario_cr()

    login(page, dados_cliente)
    acessar_funcionario(page)
    preencher_dados_gerais_funcionario(page, funcionario)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Funcionário.")
