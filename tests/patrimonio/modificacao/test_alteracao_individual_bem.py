import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.alteracao_individual_bem.navegar_para_alteracao_individual_bem_flow import (
    acessar_alteracao_individual_bem,
)
from flows.patrimonio.modificacao.alteracao_individual_bem.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_individual_bem(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração Individual do Bem.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_por_indice(19)

    login(page, dados_cliente)
    acessar_alteracao_individual_bem(page)

    if not preencher_dados_gerais(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Alteração Individual do Bem.")
