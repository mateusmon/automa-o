from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.relatorios.relatorios_financeiros.navegar_para_relatorios_financeiros_flow import (
    acessar_relatorios_financeiros,
)
from flows.patrimonio.relatorios.relatorios_financeiros.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_financeiros(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de impressão de Relatórios Financeiros.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_relatorios_financeiros(page)
    preencher_dados_gerais(page, ug)
    imprimir_relatorio(page, timeout_geracao=200_000)
    logout(page)
    
    logger.success("Finalizou teste de impressão de Relatórios Financeiros.")
