from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.conta_contabil.consultar_conta_contabil_flow import (
    consultar_conta_contabil,
)
from flows.patrimonio.auxiliares.conta_contabil.navegar_para_conta_contabil_flow import (
    acessar_conta_contabil,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_conta_contabil(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Conta Contábil.")

    dados_cliente = contexto_cliente.dados_cliente()
    bem = contexto_cliente.bem_padrao()

    login(page, dados_cliente)
    acessar_conta_contabil(page)
    consultar_conta_contabil(page, bem)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Consulta de Conta Contábil.")
