from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.financeiro.previa_rmma.navegar_para_previa_rmma_flow import (
    acessar_previa_rmma,
)
from flows.almoxarifado.financeiro.previa_rmma.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_gerar_previa_rmma(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou test de Emissão de Prévia RMMA.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_previa_rmma(page)
    preencher_dados_gerais(page, almoxarifado, ug)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Emissão de Prévia RMMA.")
