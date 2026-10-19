import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ua.alterar_ua_flow import (
    alterar_ua,
)
from flows.corporativo.estrutura_organizacional.cadastro_ua.consultar_ua_flow import (
    consultar_ua,
)
from flows.corporativo.estrutura_organizacional.cadastro_ua.navegar_para_ua_flow import (
    acessar_ua,
)
from flows.corporativo.estrutura_organizacional.cadastro_ua.selecionar_ua_flow import (
    selecionar_ua,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_ua(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de UA - Unidade Administrativa.")

    dados_cliente = contexto_cliente.dados_cliente()
    ua = contexto_cliente.unidade_administrativa_cr()

    login(page, dados_cliente)
    acessar_ua(page)
    consultar_ua(page, ua)

    if not selecionar_ua(page, ua):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_ua(page)
    logout(page)

    logger.success("Finalizou teste de Alteração de UA - Unidade Administrativa.")
