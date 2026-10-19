import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.alterar_material_flow import (
    alterar_material,
)
from flows.corporativo.material.cadastro_material_servico.navegar_para_material_servico_flow import (
    acessar_material_servico,
)
from flows.corporativo.material.consultar_material_flow import (
    consultar_material,
)
from flows.corporativo.material.selecionar_material_flow import (
    selecionar_material,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_material_servico(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Material Serviço.")

    dados_cliente = contexto_cliente.dados_cliente()
    material = contexto_cliente.material_servico_cr()

    login(page, dados_cliente)
    acessar_material_servico(page)
    consultar_material(page, material)

    if not selecionar_material(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_material(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Material Serviço.")
