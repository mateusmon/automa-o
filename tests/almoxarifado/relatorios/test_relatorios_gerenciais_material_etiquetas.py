from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.relatorios.rel_gerenciais_material_etiquetas.navegar_para_material_etiquetas_flow import (
    acessar_material_etiquetas,
)
from flows.almoxarifado.relatorios.rel_gerenciais_material_etiquetas.preencher_material_flow import (
    preencher_dados,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_gerenciais_material_etiquetas(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Rel. Gerenciais - Material - Etiquetas.")

    dados_cliente = contexto_cliente.dados_cliente()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_material_etiquetas(page)
    preencher_dados(page, material)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Rel. Gerenciais - Material - Etiquetas.")
