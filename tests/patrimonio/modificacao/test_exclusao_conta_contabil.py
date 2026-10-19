import pytest
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
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_conta_contabil(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Modificação de Conta Contábil.")

    dados_cliente = contexto_cliente.dados_cliente()
    bem = contexto_cliente.bem_por_indice(20)

    login(page, dados_cliente)
    acessar_conta_contabil(page)
    consultar_conta_contabil(page, bem)

    if not selecionar_conta_contabil(page, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Modificação de Conta Contábil.")
