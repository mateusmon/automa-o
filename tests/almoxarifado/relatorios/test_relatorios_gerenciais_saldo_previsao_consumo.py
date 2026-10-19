import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.relatorios.rel_gerenciais_saldo_previsao_consumo.navegar_para_relatorio_saldo_previsao_consumo_flow import (
    acessar_relatorio_saldo_previsao_consumo,
)
from flows.almoxarifado.relatorios.rel_gerenciais_saldo_previsao_consumo.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_saldo_previsao_consumo(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Rel. Gerenciais - Saldo de Previsão de Consumo.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)

    if not acessar_relatorio_saldo_previsao_consumo(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not preencher_dados_gerais(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Rel. Gerenciais - Saldo de Previsão de Consumo.")
