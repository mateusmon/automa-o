import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.shared.selecionar_ultima_movimentacao_flow import (
    selecionar_ultima_movimentacao,
)
from flows.patrimonio.movimentacao.transferencia_interna.consultar_transferencia_flow import (
    consultar_transferencia,
)
from flows.patrimonio.movimentacao.transferencia_interna.navegar_para_transferencia_interna_flow import (
    acessar_transferencia_interna,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_transferencia_interna(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Transferência Interna.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul_estoque = contexto_cliente.unidade_localizacao_estoque()
    ul_destino = contexto_cliente.unidade_localizacao_padrao()
    
    login(page, dados_cliente)
    acessar_transferencia_interna(page)
    consultar_transferencia(page, ug, ul_estoque, ul_destino)

    if not selecionar_ultima_movimentacao(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Transferência Interna.")
