from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.entidade_externa.cadastro_fornecedor.navegar_para_fornecedor_flow import (
    acessar_fornecedor,
)
from flows.corporativo.entidade_externa.cadastro_fornecedor.preencher_dados_gerais_fornecedor_flow import (
    preencher_dados_gerais_fornecedor,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_fornecedor(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Fornecedor.")

    dados_cliente = contexto_cliente.dados_cliente()
    fornecedor = contexto_cliente.fornecedor_cr()

    login(page, dados_cliente)
    acessar_fornecedor(page)
    preencher_dados_gerais_fornecedor(page, fornecedor)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Fornecedor.")
