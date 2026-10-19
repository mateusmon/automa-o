import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.manutencao_caracteristicas.navegar_manutencao_caracteristicas_flow import (
    acessar_manutencao_caracteristicas,
)
from flows.almoxarifado.auxiliares.manutencao_caracteristicas.preencher_caracteristicas_sem_confirmar_flow import (
    preencher_caracteristicas,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_manutencao_caracteristicas(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Manutenção das Características.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_manutencao_caracteristicas(page)

    if not preencher_caracteristicas(page):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    page.wait_for_timeout(timeout=2_000)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Consulta de Manutenção das Características.")
