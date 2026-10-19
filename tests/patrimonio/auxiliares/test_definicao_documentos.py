import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.definicao_documentos.consulta_definicao_documentos.consultar_definicao_documentos_flow import (
    consultar_definicao_documentos,
)
from flows.patrimonio.auxiliares.definicao_documentos.navegar_para_definicao_documentos_flow import (
    acessar_definicao_documentos,
)
from flows.patrimonio.auxiliares.definicao_documentos.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_definicao_documentos(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Definição dos Documentos.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_documentos(page)

    if consultar_definicao_documentos(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_dados_gerais(page)
    logout(page)
    
    logger.success("Finalizou teste de Definição dos Documentos.")