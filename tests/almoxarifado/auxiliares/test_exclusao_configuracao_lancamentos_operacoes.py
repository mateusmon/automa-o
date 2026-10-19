import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.configuracao_lancamentos_operacoes.consultar_configuracao_operacoes_flow import (
    consultar_configuracao_operacoes,
)
from flows.almoxarifado.auxiliares.configuracao_lancamentos_operacoes.navegar_para_configuracao_operacoes_flow import (
    acessar_configuracao_operacoes,
)
from flows.almoxarifado.auxiliares.configuracao_lancamentos_operacoes.selecionar_configuracao_flow import (
    selecionar_configuracao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_configuracao_lancamentos_operacoes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Configuração de Lançamentos - Operações.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_configuracao_operacoes(page)
    consultar_configuracao_operacoes(page)

    if not selecionar_configuracao(page, "AUTOMAÇÃO", posicao="last"):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not excluir_movimento(page, esperar_sucesso=True):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Configuração de Lançamentos - Operações.")
