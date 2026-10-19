from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.definicao_tipos_observacao.navegar_para_definicao_tipos_observacao_flow import (
    acessar_definicao_tipos_observacao,
)
from flows.patrimonio.auxiliares.definicao_tipos_observacao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_definicao_tipos_observacoes(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Definição dos Tipos de Observações.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_tipos_observacao(page)
    preencher_dados_gerais(page)
    logout(page)
    
    logger.success("Finalizou teste de Definição dos Tipos de Observações.")