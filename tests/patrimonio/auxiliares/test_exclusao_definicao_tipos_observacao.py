import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.definicao_tipos_observacao.consulta_definicao_tipos_observacoes.consultar_definicao_tipos_observacoes_flow import (
    consultar_definicao_tipos_observacoes,
)
from flows.patrimonio.auxiliares.definicao_tipos_observacao.navegar_para_definicao_tipos_observacao_flow import (
    acessar_definicao_tipos_observacao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_definicao_tipos_observacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão dos Tipos de Observações.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_tipos_observacao(page)

    if not consultar_definicao_tipos_observacoes(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão dos Tipos de Observações.")