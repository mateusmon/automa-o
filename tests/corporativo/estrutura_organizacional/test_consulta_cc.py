import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_cc.consultar_cc_flow import (
    consultar_cc,
)
from flows.corporativo.estrutura_organizacional.cadastro_cc.navegar_para_cc_flow import (
    acessar_cc,
)
from flows.corporativo.estrutura_organizacional.cadastro_cc.selecionar_cc_flow import (
    selecionar_cc,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_cc(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de CC - Centro de Custos.")

    dados_cliente = contexto_cliente.dados_cliente()
    cc = contexto_cliente.centro_custo_cr()

    login(page, dados_cliente)
    acessar_cc(page)
    consultar_cc(page, cc)

    if not selecionar_cc(page, cc):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)
    logout(page)

    logger.success("Finalizou teste de Consulta de CC - Centro de Custos.")
