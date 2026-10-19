from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.relatorios.relatorio_movimentacoes.navegar_para_relatorio_movimentacoes_flow import (
    acessar_relatorio_movimentacoes,
)
from flows.patrimonio.relatorios.relatorio_movimentacoes.preencher_filtro_flow import (
    preencher_filtro,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorio_movimentacoe(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Relatório de Movimentações.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_relatorio_movimentacoes(page)
    preencher_filtro(page)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Relatório de Movimentações.")