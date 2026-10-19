from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.catalogo_materiais.navegar_para_catalogo_materiais_flow import (
    acessar_catalogo_materiais,
)
from flows.patrimonio.auxiliares.catalogo_materiais.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.auxiliares.catalogo_materiais.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.patrimonio.auxiliares.catalogo_materiais.preencher_ul_flow import (
    preencher_ul,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_catalogo_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Catálogo de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()
    ul = contexto_cliente.unidade_localizacao_padrao()

    login(page, dados_cliente)
    acessar_catalogo_materiais(page)
    preencher_dados_gerais(page, ug, "CATÁLOGO DE TESTE AUTOMÁTICO")
    preencher_materiais(page, bem)
    preencher_ul(page, ul)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Catálogo de Materiais.")
