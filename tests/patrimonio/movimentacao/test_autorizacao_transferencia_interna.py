import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.autorizacao_transferencia_interna.autorizar_transferencia_interna_flow import (
    autorizar_transferencia_interna,
)
from flows.patrimonio.movimentacao.autorizacao_transferencia_interna.navegar_para_autorizacao_flow import (
    acessar_autorizacao_transferencia_interna,
)
from flows.patrimonio.movimentacao.autorizacao_transferencia_interna.selecionar_transferencia_interna_flow import (
    selecionar_transferencia_interna,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_autorizacao_transferencia_interna(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Autorização de Transferência Interna.")

    dados_cliente =  contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_padrao()
    
    login(page, dados_cliente)

    if not acessar_autorizacao_transferencia_interna(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not selecionar_transferencia_interna(page, ug, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    autorizar_transferencia_interna(page)
    logout(page)
    
    logger.success("Finalizou teste de Autorização de Transferência Interna.")