from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.modificacao_material.navegar_para_modificacao_material_flow import (
    acessar_modificacao_material,
)
from flows.patrimonio.modificacao.modificacao_material.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_modificacao_material(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Modificação de Material.")

    dados_cliente = contexto_cliente.dados_cliente()
    bem = contexto_cliente.bem_por_indice(20)
    bem_novo = contexto_cliente.bem_por_indice(1)

    login(page, dados_cliente)
    acessar_modificacao_material(page)
    preencher_dados_gerais(page, bem, bem_novo)
    logout(page)
    
    logger.success("Finalizou teste de Modificação de Material.")
