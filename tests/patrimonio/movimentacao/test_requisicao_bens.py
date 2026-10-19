import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.requisicao_bens.navegar_para_requisicao_bens_flow import (
    acessar_requisicao_bens,
)
from flows.patrimonio.movimentacao.requisicao_bens.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.requisicao_bens.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_requisicao_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Requisição de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_padrao()
    bem = contexto_cliente.bem_padrao()

    login(page, dados_cliente)

    if not acessar_requisicao_bens(page):
        logger.info("Menu 'Requisição' não disponível para o cliente. Pulando teste.")
        pytest.skip()

    preencher_dados_gerais(page, ug, ul)
    preencher_materiais(page, bem)
    logout(page)

    logger.success("Finalizou teste de Requisição de Bens.")
