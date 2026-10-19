import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.devolucao_transferencia_externa.consultar_transferencia_flow import (
    consultar_transferencia,
)
from flows.patrimonio.movimentacao.devolucao_transferencia_externa.navegar_para_devolucao_transferencia_externa_flow import (
    acessar_devolucao_transferencia_externa,
)
from flows.patrimonio.movimentacao.devolucao_transferencia_externa.preencher_bens_transferidos_flow import (
    preencher_bens_transferidos,
)
from flows.patrimonio.movimentacao.devolucao_transferencia_externa.selecionar_transferencia_flow import (
    selecionar_transferencia,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_devolucao_transferencia_externa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Devolução de Transferência Externa.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_padrao()
    funcionario = contexto_cliente.funcionario_padrao()
    
    login(page, dados_cliente)
    acessar_devolucao_transferencia_externa(page)
    consultar_transferencia(page, ug, ul)
    
    if not selecionar_transferencia(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_bens_transferidos(page, funcionario)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Devolução de Transferência Externa.")
    