from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.enderecamento_de_material.navegar_para_enderecamento_material_flow import (
    acessar_enderecamento_material,
)
from flows.almoxarifado.auxiliares.enderecamento_de_material.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_enderecamento_material(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Endereçamento de Material.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_enderecamento_material(page)
    preencher_dados_gerais(page, almoxarifado, material)
    page.wait_for_timeout(timeout=5_000)
    logout(page)

    logger.success("Finalizou teste de Consulta de Endereçamento de Material.")