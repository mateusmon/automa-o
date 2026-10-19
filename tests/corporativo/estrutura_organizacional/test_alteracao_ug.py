import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ug.alterar_ug_flow import (
    alterar_ug,
)
from flows.corporativo.estrutura_organizacional.cadastro_ug.consultar_ug_flow import (
    consultar_ug,
)
from flows.corporativo.estrutura_organizacional.cadastro_ug.navegar_para_ug_flow import (
    acessar_ug,
)
from flows.corporativo.estrutura_organizacional.cadastro_ug.selecionar_ug_flow import (
    selecionar_ug,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_ug(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de UG - Unidade Gestora.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.unidade_gestora_cr()

    login(page, dados_cliente)
    acessar_ug(page)
    consultar_ug(page, ug)

    if not selecionar_ug(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_ug(page, ug)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de UG - Unidade Gestora.")
