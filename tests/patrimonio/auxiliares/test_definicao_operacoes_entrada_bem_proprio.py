import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.definicao_operacoes.navegar_para_definicao_operacoes_flow import (
    acessar_definicao_operacoes,
)
from flows.patrimonio.auxiliares.definicao_operacoes.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_definicao_operacoes_entrada_bem_proprio(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Definição de Operações de Entrada de Bem Próprio.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_operacoes(page)

    if not preencher_dados_gerais(page, "ENTRADA DE BEM PRÓPRIO", "ENTRADA PRÓPRIA TESTE AUTOMATIZADO"):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    logout(page)

    logger.success("Finalizou teste de Definição de Operações de Entrada de Bem Próprio.")