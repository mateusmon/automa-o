import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.config_lancamentos_observacao.alterar_configuracao_observacao_flow import (
    alterar_configuracao_observacao,
)
from flows.almoxarifado.auxiliares.config_lancamentos_observacao.consultar_configuracao_observacao_flow import (
    consultar_configuracao_observacao,
)
from flows.almoxarifado.auxiliares.config_lancamentos_observacao.navegar_para_config_lancamento_observacao_flow import (
    acessar_config_observacao,
)
from flows.almoxarifado.auxiliares.config_lancamentos_observacao.selecionar_configuracao_observacao_flow import (
    selecionar_configuracao_observacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_configuracao_lancamentos_observacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Configuração de Lançamentos - Tipo de Observação.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_config_observacao(page)
    consultar_configuracao_observacao(page)

    if not selecionar_configuracao_observacao(page, "AUTOMAÇÃO"):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_configuracao_observacao(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Configuração de Lançamentos - Tipo de Observação.")
