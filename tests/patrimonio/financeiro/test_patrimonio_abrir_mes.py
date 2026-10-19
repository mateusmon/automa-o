import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.financeiro.abrir_fechar_mes.navegar_para_ano_mes_referencia_ug_flow import (
    acessar_ano_mes_referencia,
)
from flows.patrimonio.financeiro.abrir_fechar_mes.preencher_itens_flow import (
    preencher_itens,
)
from flows.patrimonio.financeiro.abrir_fechar_mes.verificar_status_flow import (
    verificar_status,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_patrimonio_abrir_mes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Abertura de Mês.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_ano_mes_referencia(page)
    preencher_itens(page, ug, "ABRIR")

    if verificar_status(page, ug) == "UG NÃO ENCONTRADA" or not verificar_status(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Abertura de Mês.")
