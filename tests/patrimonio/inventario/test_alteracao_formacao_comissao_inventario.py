import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.inventario.formacao_comissao_inventario.alterar_formacao_flow import (
    alterar_formacao,
)
from flows.patrimonio.inventario.formacao_comissao_inventario.consultar_formacao_flow import (
    consultar_formacao,
)
from flows.patrimonio.inventario.formacao_comissao_inventario.navegar_para_formacao_comissao_inventario_flow import (
    acessar_formacao_comissao_inventario,
)
from flows.patrimonio.inventario.formacao_comissao_inventario.selecionar_formacao_flow import (
    selecionar_formacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_formacao_comissao_inventario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteracao de Formação de Comissão de Inventário.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_formacao_comissao_inventario(page)
    consultar_formacao(page, ug)

    if not selecionar_formacao(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_formacao(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteracao de Formação de Comissão de Inventário.")
