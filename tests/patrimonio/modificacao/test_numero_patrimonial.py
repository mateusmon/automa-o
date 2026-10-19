import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.numero_patrimonial.navegar_para_numero_patrimonial_flow import (
    acessar_numero_patrimonial,
)
from flows.patrimonio.modificacao.numero_patrimonial.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_numero_patrimonial(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Modificação de Número Patrimonial.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_por_indice(19)

    login(page, dados_cliente)
    acessar_numero_patrimonial(page)

    if not preencher_dados_gerais(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Modificação de Número Patrimonial.")
