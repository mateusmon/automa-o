import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.valor_mercado.navegar_para_valor_mercado_flow import (
    acessar_valor_mercado,
)
from flows.patrimonio.modificacao.valor_mercado.preencher_bem_flow import preencher_bem
from flows.patrimonio.modificacao.valor_mercado.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_valor_mercado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Valor de Mercado.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_por_indice(19)

    login(page, dados_cliente)
    acessar_valor_mercado(page)
    preencher_dados_gerais(page, ug)

    if not preencher_bem(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    logout(page)
    
    logger.success("Finalizou teste de Valor de Mercado.")
