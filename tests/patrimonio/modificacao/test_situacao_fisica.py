import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.situacao_fisica.navegar_para_situacao_fisica_flow import (
    acessar_situacao_fisica,
)
from flows.patrimonio.modificacao.situacao_fisica.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.modificacao.situacao_fisica.preencher_patrimonios_flow import (
    preencher_patrimonios,
)
from flows.patrimonio.modificacao.situacao_fisica.selecionar_situacao_flow import (
    selecionar_situacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_situacao_fisica(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Modificação da Situação Física de Bem.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_por_indice(19)

    login(page, dados_cliente)
    
    if not acessar_situacao_fisica(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_dados_gerais(page, ug)

    if not preencher_patrimonios(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    situacao_fisica = selecionar_situacao(page, False)

    logger.info("Desfazendo modificação.")
    preencher_dados_gerais(page, ug)
    preencher_patrimonios(page, ug, bem)
    selecionar_situacao(page, True, situacao_fisica)
    logout(page)
    
    logger.success("Finalizou teste de Modificação da Situação Física de Bem.")
