import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.adicao_bem_principal.analisar_bens_adicionados_flow import (
    analisar_bens_adicionados,
)
from flows.patrimonio.movimentacao.adicao_bem_principal.consultar_bens_flow import (
    consultar_bens,
)
from flows.patrimonio.movimentacao.adicao_bem_principal.navegar_para_adicao_bem_principal_flow import (
    acessar_adicao_bem_principal,
)
from flows.patrimonio.movimentacao.adicao_bem_principal.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.adicao_bem_principal.selecionar_bem_flow import (
    selecionar_bem,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_adicao_bem_principal(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    logger.info("Iniciou teste de Consulta de Adição a Bem Principal.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_por_indice(1)
    bem_principal = contexto_cliente.bem_por_indice(2)

    login(page, dados_cliente)
    acessar_adicao_bem_principal(page)
    preencher_dados_gerais(page, ug)
    consultar_bens(page, ul, bem_principal)

    if not selecionar_bem(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not analisar_bens_adicionados(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(5_000)
    logout(page)

    logger.success("Finalizou teste de Consulta de Adição a Bem Principal.")
