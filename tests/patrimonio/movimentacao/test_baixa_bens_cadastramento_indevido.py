import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.baixa_bens.doacao.navegar_para_baixa_bens_flow import (
    acessar_baixa_bens,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.preencher_itens_flow import (
    preencher_itens,
)
from flows.patrimonio.movimentacao.baixa_bens.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.baixa_bens.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_baixa_bens_cadastramento_indevido(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Baixa de Bens por Cadastramento Indevido.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    fornecedor = contexto_cliente.fornecedor_padrao()
    bem = contexto_cliente.bem_padrao()
    
    login(page, dados_cliente)
    acessar_baixa_bens(page)
    preencher_dados_gerais(page, ug, "PRÓPRIO CONTABILIZADO", "INDEVIDO")
    preencher_documentos(page, fornecedor)

    if not preencher_itens(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    imprimir_relatorio(page, timeout_geracao=250_000)
    logout(page)
    
    logger.success("Finalizou teste de Baixa de Bens por Cadastramento Indevido.")
