from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.relatorios.relatorio_solicitados_patrimonio.navegar_para_relatorio_solicitados_patrimonio import (
    acessar_relatorio_solicitados_patrimonio,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorio_solicitados_patrimonio(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Relatórios Solicitados Patrimônio.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_relatorio_solicitados_patrimonio(page)
    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Relatório Solicitados Patrimônio.")
