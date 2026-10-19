from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.financeiro.resumo_mensal_bens.abrir_fechar_mes_pcdf.preencher_detalhamento_flow import (
    preencher_detalhamento,
)
from flows.patrimonio.financeiro.resumo_mensal_bens.navegar_para_rmb_flow import (
    acessar_rmb,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout

# from flows.patrimonio.financeiro.resumo_mensal_bens.imprimir_relatorio_flow import imprimir_relatorio


def test_fechar_mes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Fechamento de Mês.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_rmb(page)
    preencher_detalhamento(page, ug, "FECHAR")

    # Esperando até 10 minutos pra fechar o mês
    imprimir_relatorio(page, timeout_geracao=600_000)
    logout(page)
    
    logger.success("Finalizou teste de Fechamento de Mês.")
