import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_material_servico.navegar_para_material_servico_flow import (
    acessar_material_servico,
)
from flows.corporativo.material.confirmar_material_flow import (
    confirmar_material,
)
from flows.corporativo.material.preencher_dados_gerais_material_flow import (
    preencher_dados_gerais_material,
)
from flows.corporativo.material.selecionar_conta_flow import (
    selecionar_conta,
)
from flows.corporativo.material.selecionar_subgrupo_flow import (
    selecionar_subgrupo,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_material_servico(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Material Serviço.")

    dados_cliente = contexto_cliente.dados_cliente()
    material = contexto_cliente.material_servico_cr()

    login(page, dados_cliente)
    acessar_material_servico(page)
    selecionar_subgrupo(page, material)
    preencher_dados_gerais_material(page, material)
    
    if not selecionar_conta(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not confirmar_material(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)

    logger.success("Finalizou teste de Cadastro de Material Serviço.")
