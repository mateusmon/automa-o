from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.config_lancamento_documentacao.navegar_pagina_config_lancamento_documentacao_flow import (
    acessar_config_documentacao,
)
from flows.almoxarifado.auxiliares.config_lancamento_documentacao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_configuracao_lancamentos_documentacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Configuração de Lançamentos - Documentação.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_config_documentacao(page)
    preencher_dados_gerais(page)
    page.wait_for_timeout(3_000)
    logout(page)

    logger.success("Finalizou teste de Configuração de Lançamentos - Documentação.")
