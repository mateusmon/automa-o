import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.entidade_externa.cadastro_fornecedor.consultar_fornecedor_flow import (
    consultar_fornecedor,
)
from flows.corporativo.entidade_externa.cadastro_fornecedor.navegar_para_fornecedor_flow import (
    acessar_fornecedor,
)
from flows.corporativo.entidade_externa.cadastro_fornecedor.selecionar_fornecedor_flow import (
    selecionar_fornecedor,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_fornecedor(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Fornecedor.")

    dados_cliente = contexto_cliente.dados_cliente()
    fornecedor = contexto_cliente.fornecedor_cr()

    login(page, dados_cliente)
    acessar_fornecedor(page)
    consultar_fornecedor(page, fornecedor)

    if not selecionar_fornecedor(page, fornecedor):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Fornecedor.")
