from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.relatorios.rel_gerenciais_saidas.navegar_para_rel_gerenciais_saidas_flow import (
    acessar_rel_gerenciais_saidas,
)
from flows.almoxarifado.relatorios.rel_gerenciais_saidas.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_relatorios_gerenciais_saidas(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Rel. Gerenciais - Saídas.")
    
    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_rel_gerenciais_saidas(page)
    preencher_dados_gerais(page, ug, almoxarifado)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Rel. Gerenciais - Saídas.")
