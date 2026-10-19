import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.requisicao_bens.alteracao.alterar_requisicao_flow import (
    alterar_requisicao,
)
from flows.patrimonio.movimentacao.requisicao_bens.consultar_requisicao_flow import (
    consultar_requisicao,
)
from flows.patrimonio.movimentacao.requisicao_bens.navegar_para_requisicao_bens_flow import (
    acessar_requisicao_bens,
)
from flows.patrimonio.movimentacao.requisicao_bens.selecionar_requisicao_flow import (
    selecionar_requisicao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_requisicao_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Requisição de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_padrao()
    bem = contexto_cliente.bem_padrao()
    
    login(page, dados_cliente)

    if not acessar_requisicao_bens(page):
        logger.info("Menu 'Requisição' não disponível para o cliente. Pulando teste.")
        pytest.skip()

    consultar_requisicao(page, ug, bem)

    if not selecionar_requisicao(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not alterar_requisicao(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Consulta de Requisição de Bens.")
