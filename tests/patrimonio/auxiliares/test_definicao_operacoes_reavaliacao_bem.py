import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.definicao_operacoes.consulta_operacao.consultar_operacao_flow import (
    consultar_operacao,
)
from flows.patrimonio.auxiliares.definicao_operacoes.navegar_para_definicao_operacoes_flow import (
    acessar_definicao_operacoes,
)
from flows.patrimonio.auxiliares.definicao_operacoes.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_definicao_operacoes_reavaliacao_bem(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Definição de Operações de Reavaliação de Bem.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_operacoes(page)

    if not preencher_dados_gerais(page, "REAVALIACAO DE BEM", "REAVALIAÇÃO TESTE AUTOMATIZADO"):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not consultar_operacao(page, "REAVALIACAO DE BEM", "REAVALIAÇÃO TESTE AUTOMATIZADO"):
        logger.warning("Pulando teste.")
        pytest.skip()

    logger.info("Desfazendo movimento.")
    excluir_movimento(page)
    logout(page)

    logger.success("Finalizou teste de Definição de Operações de Reavaliação de Bem.")