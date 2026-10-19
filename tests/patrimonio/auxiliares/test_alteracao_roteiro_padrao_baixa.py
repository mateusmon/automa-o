import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.alterar_roteiro_padrao_baixa_flow import (
    alterar_roteiro_padrao_baixa,
)
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.consultar_roteiro_padrao_baixa_flow import (
    consultar_roteiro_padrao_baixa,
)
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.navegar_para_roteiro_padrao_baixa_flow import (
    acessar_roteiro_padrao_baixa,
)
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.selecionar_roteiro_padrao_baixa_flow import (
    selecionar_roteiro_padrao_baixa,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_roteiro_padrao_baixa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Roteiro Padrão para Baixa.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_roteiro_padrao_baixa(page):
        logger.info("Pulado teste.")
        pytest.skip()
        
    consultar_roteiro_padrao_baixa(page)

    if not selecionar_roteiro_padrao_baixa(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_roteiro_padrao_baixa(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Roteiro Padrão para Baixa.")
