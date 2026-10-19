import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.detentor_bem_cadastro.consultar_cadastros_flow import (
    consultar_cadastros,
)
from flows.patrimonio.modificacao.detentor_bem_cadastro.navegar_para_detentor_bem_cadastro_flow import (
    acessar_detentor_bem_cadastro,
)
from flows.patrimonio.modificacao.detentor_bem_cadastro.selecionar_cadastro_flow import (
    selecionar_cadastro,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_detentor_bem_cadastro(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Cadastro de Detentor do Bem.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    funcionario = contexto_cliente.funcionario_padrao()

    login(page, dados_cliente)
    acessar_detentor_bem_cadastro(page)
    consultar_cadastros(page, ug)

    if not selecionar_cadastro(page, funcionario):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Cadastro de Detentor do Bem.")
