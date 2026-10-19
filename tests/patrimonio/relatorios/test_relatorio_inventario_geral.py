from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.relatorios.relatorio_inventario_geral.navegar_para_relatorio_inventario_geral_flow import (
    acessar_relatorio_inventario_geral,
)
from flows.patrimonio.relatorios.relatorio_inventario_geral.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorio_inventario_geral(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de impressão de Relatório de Inventário Geral.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_relatorio_inventario_geral(page)
    preencher_dados_gerais(page, ug)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de impressão de Relatório de Inventário Geral.")
