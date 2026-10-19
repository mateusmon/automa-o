import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.transferencia_externa.confirmar_transferencia_externa_flow import (
    confirmar_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.navegar_para_transferencia_externa import (
    acessar_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.preencher_bens_a_transferir_flow import (
    preencher_bens_transferir,
)
from flows.patrimonio.movimentacao.transferencia_externa.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_transferencia_externa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Transferência Externa.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()
    fornecedor = contexto_cliente.fornecedor_padrao()
    funcionario = contexto_cliente.funcionario_padrao()
    
    login(page, dados_cliente)
    acessar_transferencia_externa(page)
    preencher_dados_gerais(page, ug, fornecedor, funcionario)
    
    if not preencher_bens_transferir(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    confirmar_transferencia_externa(page)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Transferência Externa.")
    