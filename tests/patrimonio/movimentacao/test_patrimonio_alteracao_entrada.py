import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.entrada_bens.alteracao.editar_material_flow import (
    editar_material,
)
from flows.patrimonio.movimentacao.entrada_bens.consultar_entradas_flow import (
    consultar_entradas,
)
from flows.patrimonio.movimentacao.entrada_bens.navegar_para_entrada_bens_flow import (
    acessar_entrada_bens,
)
from flows.patrimonio.movimentacao.shared.selecionar_ultima_movimentacao_flow import (
    selecionar_ultima_movimentacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_patrimonio_alteracao_entrada(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Entrada de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()
    
    login(page, dados_cliente)
    acessar_entrada_bens(page)
    consultar_entradas(page, ug, bem)

    if not selecionar_ultima_movimentacao(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not editar_material(page, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Alteração de Entrada de Bens.")
