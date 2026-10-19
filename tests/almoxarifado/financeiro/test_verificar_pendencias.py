import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.financeiro.fazer_operacao_flow import conseguiu_fazer_operacao
from flows.almoxarifado.financeiro.fechar_mes.navegar_para_fechar_mes_flow import (
    acessar_fechar_mes,
)
from flows.almoxarifado.financeiro.pendencias.exibir_pendencias_flow import (
    exibir_pendencias,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_verificar_pendencias(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Verificação de Pendências de UG.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_fechar_mes(page)

    if not conseguiu_fazer_operacao(page, ug, "PENDÊNCIAS"):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    exibir_pendencias(page)
    logout(page)
    
    logger.success("Finalizou teste de Verificação de Pendências de UG.")
