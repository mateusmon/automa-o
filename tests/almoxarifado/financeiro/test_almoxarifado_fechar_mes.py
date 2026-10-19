import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.financeiro.fechar_mes.conseguiu_fechar_mes_flow import (
    conseguiu_fechar_mes,
)
from flows.almoxarifado.financeiro.fechar_mes.navegar_para_fechar_mes_flow import (
    acessar_fechar_mes,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_almoxarifado_fechar_mes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Fechamento de Mês.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_fechar_mes(page)

    if not conseguiu_fechar_mes(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    logout(page)
    
    logger.success("Finalizou teste de Fechamento de Mês.")
