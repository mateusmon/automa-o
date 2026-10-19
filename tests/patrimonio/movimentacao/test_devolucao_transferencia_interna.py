import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.devolucao_transferencia_interna.consultar_transferencia_flow import (
    consultar_transferencia,
)
from flows.patrimonio.movimentacao.devolucao_transferencia_interna.devolver_transferencia_flow import (
    devolver_transferencia,
)
from flows.patrimonio.movimentacao.devolucao_transferencia_interna.navegar_para_devolucao_transferencia_interna_flow import (
    acessar_devolucao_transferencia_interna,
)
from flows.patrimonio.movimentacao.devolucao_transferencia_interna.selecionar_transferencia_flow import (
    selecionar_transferencia,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_devolucao_transferencia_interna(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Devolução de Transferência Interna.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_por_indice(1)
        
    login(page, dados_cliente)

    if not acessar_devolucao_transferencia_interna(page):
        logger.warning("Menu 'Devolução' não disponível para o cliente. Pulando teste.")
        pytest.skip()

    consultar_transferencia(page, ug, ul)

    if not selecionar_transferencia(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    devolver_transferencia(page, ul)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Devolução de Transferência Interna.")
