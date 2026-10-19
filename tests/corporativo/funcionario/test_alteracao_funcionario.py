import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcionario.alterar_funcionario_flow import (
    alterar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.consultar_funcionario_flow import (
    consultar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.navegar_para_funcionario_flow import (
    acessar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.selecionar_funcionario_flow import (
    selecionar_funcionario,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_funcionario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Funcionário.")

    dados_cliente = contexto_cliente.dados_cliente()
    funcionario = contexto_cliente.funcionario_cr()

    login(page, dados_cliente)
    acessar_funcionario(page)
    consultar_funcionario(page, funcionario)

    if not selecionar_funcionario(page, funcionario):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_funcionario(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Funcionário.")
