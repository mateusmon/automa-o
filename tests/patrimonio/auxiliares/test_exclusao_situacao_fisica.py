import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.situacao_fisica.consultar_situacao_fisica_flow import (
    consultar_situacao_fisica,
)
from flows.patrimonio.auxiliares.situacao_fisica.navegar_para_situacao_fisica_flow import (
    acessar_situacao_fisica,
)
from flows.patrimonio.auxiliares.situacao_fisica.selecionar_situacao_fisica_flow import (
    selecionar_situacao_fisica,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_situacao_fisica(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Situação Física.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_situacao_fisica(page):
        logger.warning("Pulando teste.")
        pytest.skip()
        
    consultar_situacao_fisica(page, "METAFÍSICO")

    if not selecionar_situacao_fisica(page, "METAFÍSICO"):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Situação Física.")
