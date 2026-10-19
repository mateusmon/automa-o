import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_material_permanente.navegar_para_material_permanente_flow import (
    acessar_material_permanente,
)
from flows.corporativo.material.consultar_material_flow import (
    consultar_material,
)
from flows.corporativo.material.selecionar_material_flow import (
    selecionar_material,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_material_permanente(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Material Permanente.")

    dados_cliente = contexto_cliente.dados_cliente()
    material = contexto_cliente.material_permanente_cr()

    login(page, dados_cliente)
    acessar_material_permanente(page)
    consultar_material(page, material)

    if not selecionar_material(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Material Permanente.")
