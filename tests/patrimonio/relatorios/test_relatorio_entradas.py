from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.relatorios.relatorio_entradas.navegar_para_relatorio_entradas_flow import (
    acessar_relatorio_entradas,
)
from flows.patrimonio.relatorios.relatorio_entradas.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorio_entradas(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Relatório de Entradas.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_relatorio_entradas(page)
    preencher_dados_gerais(page, ug)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Relatório de Entradas.")