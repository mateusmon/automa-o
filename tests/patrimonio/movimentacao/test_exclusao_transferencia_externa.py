import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.shared.selecionar_ultima_movimentacao_flow import (
    selecionar_ultima_movimentacao,
)
from flows.patrimonio.movimentacao.transferencia_externa.consultar_transferencia_flow import (
    consultar_transferencia,
)
from flows.patrimonio.movimentacao.transferencia_externa.navegar_para_transferencia_externa import (
    acessar_transferencia_externa,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_transferencia_externa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Transferência Externa.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    
    login(page, dados_cliente)
    acessar_transferencia_externa(page)
    consultar_transferencia(page, ug)

    if not selecionar_ultima_movimentacao(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Transferência Externa.")