# Não é possível criar uma conta contábil aqui, apenas consultar

from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.configuracao_lancamentos_operacoes.escolher_documentos_flow import (
    escolher_documentos,
)
from flows.almoxarifado.auxiliares.configuracao_lancamentos_operacoes.navegar_para_configuracao_operacoes_flow import (
    acessar_configuracao_operacoes,
)
from flows.almoxarifado.auxiliares.configuracao_lancamentos_operacoes.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_configuracao_lancamentos_operacoes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Configuração de Lançamentos - Operações.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_configuracao_operacoes(page)
    preencher_dados_gerais(page)
    escolher_documentos(page)
    logout(page)
    
    logger.success("Finalizou teste de Configuração de Lançamentos - Operações.")
