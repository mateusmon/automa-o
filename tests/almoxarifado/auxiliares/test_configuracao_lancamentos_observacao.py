from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.config_lancamentos_observacao.navegar_para_config_lancamento_observacao_flow import (
    acessar_config_observacao,
)
from flows.almoxarifado.auxiliares.config_lancamentos_observacao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_configuracoes_lancamentos_observacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Configuração de Lançamentos - Tipo de Observação.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_config_observacao(page)
    preencher_dados_gerais(page)
    logout(page)
    
    logger.success("Finalizou teste de Configuração de Lançamentos - Tipo de Observação.")
