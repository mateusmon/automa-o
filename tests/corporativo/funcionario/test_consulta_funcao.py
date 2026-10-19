import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcao.consultar_funcao_flow import (
    consultar_funcao,
)
from flows.corporativo.funcionario.cadastro_funcao.navegar_para_funcao_flow import (
    acessar_funcao,
)
from flows.corporativo.funcionario.cadastro_funcao.selecionar_funcao_flow import (
    selecionar_funcao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_funcao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Função.")

    dados_cliente = contexto_cliente.dados_cliente()
    funcao = contexto_cliente.funcao_cr()

    login(page, dados_cliente)
    acessar_funcao(page)
    consultar_funcao(page, funcao)

    if not selecionar_funcao(page, funcao):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Função.")
