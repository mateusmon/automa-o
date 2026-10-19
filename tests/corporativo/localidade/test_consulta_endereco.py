import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_endereco.consultar_endereco_flow import (
    consultar_endereco,
)
from flows.corporativo.localidade.cadastro_endereco.navegar_para_endereco_flow import (
    acessar_endereco,
)
from flows.corporativo.localidade.cadastro_endereco.selecionar_endereco_flow import (
    selecionar_endereco,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_endereco(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Endereço.")

    dados_cliente = contexto_cliente.dados_cliente()
    endereco = contexto_cliente.endereco_cr()

    login(page, dados_cliente)
    acessar_endereco(page)
    consultar_endereco(page, endereco)

    if not selecionar_endereco(page, endereco):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Endereço.")
