import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.adicao_bem_principal.consultar_bens_flow import (
    consultar_bens,
)
from flows.patrimonio.movimentacao.adicao_bem_principal.consultar_num_patrimonial_flow import (
    consultar_num_patrimonial,
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
from flows.shared.confirmar_movimentacao_flow import confirmar_movimentacao
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from flows.shared.retornar_flow import retornar


def test_adicao_bem_principal(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Adição a Bem Principal.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_por_indice(1)
    bem_principal = contexto_cliente.bem_por_indice(2)
    bem_adicionado = contexto_cliente.bem_por_indice(3)

    login(page, dados_cliente)
    acessar_adicao_bem_principal(page)
    preencher_dados_gerais(page, ug)
    consultar_bens(page, ul, bem_principal)

    if not selecionar_bem(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    consultar_num_patrimonial(page, ul, bem_adicionado)

    if not selecionar_bem(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    confirmar_movimentacao(page)
    imprimir_relatorio(page)
    retornar(page)
    logout(page)

    logger.success("Finalizou teste de Adição a Bem Principal.")
