from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.relatorios.rel_gerenciais_fornecedor_materiais.navegar_para_rel_fornecedor_materiais_flow import (
    acessar_rel_fornecedor_materiais,
)
from flows.almoxarifado.relatorios.rel_gerenciais_fornecedor_materiais.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_gerenciais_fornecedor_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Rel. Gerenciais - Fornecedor / Materiais Vendidos.")

    dados_cliente = contexto_cliente.dados_cliente()
    fornecedor = contexto_cliente.fornecedor_padrao()
    
    login(page, dados_cliente)
    acessar_rel_fornecedor_materiais(page)
    preencher_dados_gerais(page, fornecedor)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Rel. Gerenciais - Fornecedor / Materiais Vendidos.")
