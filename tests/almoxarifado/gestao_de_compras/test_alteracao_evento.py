import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.evento.alteracao_evento.alterar_evento_flow import (
    alterar_evento,
)
from flows.almoxarifado.gestao_de_compras.evento.consulta_evento.consultar_evento_flow import (
    consultar_evento,
)
from flows.almoxarifado.gestao_de_compras.evento.navegar_para_evento_flow import (
    acessar_evento,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_evento(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Evento.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_evento(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not consultar_evento(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_evento(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Evento.")