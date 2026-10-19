import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.evento.consulta_evento.consultar_evento_flow import (
    consultar_evento,
)
from flows.almoxarifado.gestao_de_compras.evento.navegar_para_evento_flow import (
    acessar_evento,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_evento(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Evento.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_evento(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not consultar_evento(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Evento.")
