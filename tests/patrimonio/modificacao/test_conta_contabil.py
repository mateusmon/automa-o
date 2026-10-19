from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.conta_contabil.consulta_conta_contabil.consultar_conta_contabil_flow import (
    consultar_conta_contabil,
)
from flows.patrimonio.modificacao.conta_contabil.consulta_conta_contabil.selecionar_conta_contabil_flow import (
    selecionar_conta_contabil,
)
from flows.patrimonio.modificacao.conta_contabil.navegar_para_conta_contabil_flow import (
    acessar_conta_contabil,
)
from flows.patrimonio.modificacao.conta_contabil.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_conta_contabil(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Modificação de Conta Contábil.")

    dados_cliente = contexto_cliente.dados_cliente()
    bem = contexto_cliente.bem_por_indice(20)

    login(page, dados_cliente)
    acessar_conta_contabil(page)
    preencher_dados_gerais(page, bem)
    consultar_conta_contabil(page, bem)
    selecionar_conta_contabil(page, bem)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Modificação de Conta Contábil.")
