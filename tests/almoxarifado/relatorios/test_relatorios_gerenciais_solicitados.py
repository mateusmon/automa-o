from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.relatorios.rel_gerenciais_solicitados.navegar_para_rel_solicitados_flow import (
    acessar_rel_solicitados,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_gerenciais_solicitados(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Rel. Gerenciais - Solicitados.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_rel_solicitados(page)
    page.wait_for_timeout(5_000)
    logout(page)

    logger.success("Finalizou teste de Rel. Gerenciais - Solicitados.")
