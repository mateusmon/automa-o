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
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_definicao_operacoes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Definição de Operações.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_operacoes(page)

    if not consultar_operacao(page, "ENTRADA DE BEM PRÓPRIO", "ENTRADA PRÓPRIA TESTE AUTOMATIZADO"):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, True)
    logout(page)
    logger.success("Finalizou teste de Exclusão de Definição de Operações.")