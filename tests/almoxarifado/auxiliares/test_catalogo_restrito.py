from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.catalogo_restrito.navegar_para_catalogo_restrito_flow import (
    acessar_catalogo_restrito,
)
from flows.almoxarifado.auxiliares.catalogo_restrito.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.auxiliares.catalogo_restrito.selecionar_materiais_flow import (
    selecionar_materiais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_catalogo_restrito(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Criação de Catálogo Restrito.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_catalogo_restrito(page)
    preencher_dados_gerais(page, almoxarifado)
    selecionar_materiais(page)
    logout(page)
    
    logger.success("Finalizou teste de Criação de Catálogo Restrito.")
