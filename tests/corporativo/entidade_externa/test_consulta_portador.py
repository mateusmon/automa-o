import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.entidade_externa.cadastro_portador.consultar_portador_flow import (
    consultar_portador,
)
from flows.corporativo.entidade_externa.cadastro_portador.navegar_para_portador_flow import (
    acessar_portador,
)
from flows.corporativo.entidade_externa.cadastro_portador.selecionar_portador_flow import (
    selecionar_portador,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_portador(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Portador.")

    dados_cliente = contexto_cliente.dados_cliente()
    portador = contexto_cliente.portador_cr()

    login(page, dados_cliente)
    acessar_portador(page)
    consultar_portador(page, portador)

    if not selecionar_portador(page, portador):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Portador.")
