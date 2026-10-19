import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.termo_responsabilidade.recebimento_termo_responsabilidade.consulta_recebimento_termo_responsabilidade.consultar_recebimento_termo_responsabilidade_flow import (
    consultar_recebimento_termo_responsabilidade,
)
from flows.patrimonio.termo_responsabilidade.recebimento_termo_responsabilidade.navegar_para_recebimento_termo_responsabilidade_flow import (
    acessar_recebimento_termo_responsabilidade,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_recebimento_termo_responsabilidade(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Recebimento do Termo de Responsabilidade.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_recebimento_termo_responsabilidade(page)

    if not consultar_recebimento_termo_responsabilidade(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Recebimento do Termo de Respnsabilidade.")