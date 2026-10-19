import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.selecao_bens.alteracao.alterar_selecao_bens_flow import (
    alterar_selecao_bens,
)
from flows.patrimonio.movimentacao.selecao_bens.consultar_selecao_bens_flow import (
    consultar_selecao_bens,
)
from flows.patrimonio.movimentacao.selecao_bens.navegar_para_selecao_bens_flow import (
    acessar_selecao_bens,
)
from flows.patrimonio.movimentacao.selecao_bens.selecionar_ultima_selecao_bens_flow import (
    selecionar_ultima_selecao_bens,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_selecao_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Seleção de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    
    login(page, dados_cliente)
    acessar_selecao_bens(page)
    consultar_selecao_bens(page, ug)
    
    if not selecionar_ultima_selecao_bens(page):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    alterar_selecao_bens(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Seleção de Bens.")
