from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.relatorios.grafico_distribuicao_aquisicoes.navegar_para_grafico_aquisicoes_flow import (
    acessar_grafico_aquisicoes,
)
from flows.patrimonio.relatorios.shared.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_grafico_distribuicao_aquisicoes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de impressão de Gráfico de Distribuição das Aquisições.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_grafico_aquisicoes(page)
    preencher_dados_gerais(page, ug)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de impressão de Gráfico de Distribuição das Aquisições.")
