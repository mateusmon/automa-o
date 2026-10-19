import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.status_bem.consultar_modificacao_flow import (
    consultar_modificacao,
)
from flows.patrimonio.modificacao.status_bem.navegar_para_status_bem_flow import (
    acessar_status_bem,
)
from flows.patrimonio.modificacao.status_bem.selecionar_modificacao_flow import (
    selecionar_modificacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_status_bem(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Modificação do Status de Bem.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_status_bem(page)
    consultar_modificacao(page, ug)
    
    if not selecionar_modificacao(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Modificação do Status de Bem.")
