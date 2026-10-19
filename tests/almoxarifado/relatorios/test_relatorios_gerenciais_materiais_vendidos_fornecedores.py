from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.relatorios.rel_gerenciais_materiais_vendidos_fornecedores.navegar_para_rel_materiais_vendidos_fornecedores_flow import (
    acessar_rel_materiais_vendidos_fornecedores,
)
from flows.almoxarifado.relatorios.rel_gerenciais_materiais_vendidos_fornecedores.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_gerenciais_materiais_vendidos_fornecedores(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Rel. Gerenciais - Materiais Vendidos/Fornecedores.")

    dados_cliente = contexto_cliente.dados_cliente()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_rel_materiais_vendidos_fornecedores(page)
    preencher_dados_gerais(page, material)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Rel. Gerenciais - Materiais Vendidos/Fornecedores.")
