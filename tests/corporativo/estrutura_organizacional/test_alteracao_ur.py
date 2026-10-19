import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ur.alterar_ur_flow import (
    alterar_ur,
)
from flows.corporativo.estrutura_organizacional.cadastro_ur.consultar_ur_flow import (
    consultar_ur,
)
from flows.corporativo.estrutura_organizacional.cadastro_ur.navegar_para_ur_flow import (
    acessar_ur,
)
from flows.corporativo.estrutura_organizacional.cadastro_ur.selecionar_ur_flow import (
    selecionar_ur,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_ur(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de UR - Unidade de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.unidade_requisicao_cr()

    login(page, dados_cliente)
    acessar_ur(page)
    consultar_ur(page, ur)

    if not selecionar_ur(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_ur(page)
    logout(page)

    logger.success("Finalizou teste de Alteração de UR - Unidade de Requisição.")
