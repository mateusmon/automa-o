import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.entidade_externa.cadastro_orgao_externo.alterar_orgao_externo_flow import (
    alterar_orgao_externo,
)
from flows.corporativo.entidade_externa.cadastro_orgao_externo.consultar_orgao_externo_flow import (
    consultar_orgao_externo,
)
from flows.corporativo.entidade_externa.cadastro_orgao_externo.navegar_para_orgao_externo_flow import (
    acessar_orgao_externo,
)
from flows.corporativo.entidade_externa.cadastro_orgao_externo.selecionar_orgao_externo_flow import (
    selecionar_orgao_externo,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_orgao_externo(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Órgão Externo.")

    dados_cliente = contexto_cliente.dados_cliente()
    orgao_externo = contexto_cliente.orgao_externo_cr()

    login(page, dados_cliente)
    acessar_orgao_externo(page)
    consultar_orgao_externo(page, orgao_externo)

    if not selecionar_orgao_externo(page, orgao_externo):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_orgao_externo(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Órgão Externo.")
