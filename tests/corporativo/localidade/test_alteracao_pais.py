import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_pais.alterar_pais_flow import alterar_pais
from flows.corporativo.localidade.cadastro_pais.consultar_pais_flow import (
    consultar_pais,
)
from flows.corporativo.localidade.cadastro_pais.navegar_para_pais_flow import (
    acessar_pais,
)
from flows.corporativo.localidade.cadastro_pais.selecionar_pais_flow import (
    selecionar_pais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_pais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de País.")

    dados_cliente = contexto_cliente.dados_cliente()
    pais = contexto_cliente.pais_cr()

    login(page, dados_cliente)
    acessar_pais(page)
    consultar_pais(page, pais)

    if not selecionar_pais(page, pais):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_pais(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de País.")
