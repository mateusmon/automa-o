import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_supply.consultar_subgrupo_supply_flow import (
    consultar_subgrupo_supply,
)
from flows.corporativo.material.cadastro_supply.navegar_para_supply_flow import (
    acessar_supply,
)
from flows.corporativo.material.cadastro_supply.selecionar_subgrupo_supply_flow import (
    selecionar_subgrupo_supply,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_supply(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Supply.")

    dados_cliente = contexto_cliente.dados_cliente()
    supply = contexto_cliente.supply_cr()

    login(page, dados_cliente)

    if not acessar_supply(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    consultar_subgrupo_supply(page, supply)

    if not selecionar_subgrupo_supply(page, supply):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Supply.")
