import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.config_lancamento_documentacao.consultar_configuracao_documentacao_flow import (
    consultar_configuracao_documentacao,
)
from flows.almoxarifado.auxiliares.config_lancamento_documentacao.navegar_pagina_config_lancamento_documentacao_flow import (
    acessar_config_documentacao,
)
from flows.almoxarifado.auxiliares.config_lancamento_documentacao.selecionar_configuracao_documentacao_flow import (
    selecionar_configuracao_documentacao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_configuracao_lancamentos_documentacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Configuração de Lançamentos - Documentação.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_config_documentacao(page)
    consultar_configuracao_documentacao(page)

    if not selecionar_configuracao_documentacao(page, "AUTOMAÇÃO"):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not excluir_movimento(page, esperar_sucesso=True):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    logout(page)

    logger.success("Finalizou teste de Exclusão de Configuração de Lançamentos - Documentação.")
