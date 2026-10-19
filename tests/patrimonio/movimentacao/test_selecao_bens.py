import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.selecao_bens.confirmar_selecao_flow import (
    confirmar_selecao,
)
from flows.patrimonio.movimentacao.selecao_bens.navegar_para_selecao_bens_flow import (
    acessar_selecao_bens,
)
from flows.patrimonio.movimentacao.selecao_bens.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.selecao_bens.selecionar_bem_flow import (
    selecionar_bem,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_selecao_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Seleção de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()

    login(page, dados_cliente)
    acessar_selecao_bens(page)
    preencher_dados_gerais(page, ug)

    if not selecionar_bem(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    confirmar_selecao(page)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Seleção de Bens!")
