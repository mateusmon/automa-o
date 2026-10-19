import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.consultar_roteiro_padrao_baixa_flow import (
    consultar_roteiro_padrao_baixa,
)
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.navegar_para_roteiro_padrao_baixa_flow import (
    acessar_roteiro_padrao_baixa,
)
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.auxiliares.roteiro_padrao_baixa.selecionar_roteiro_padrao_baixa_flow import (
    selecionar_roteiro_padrao_baixa,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_roteiro_padrao_baixa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Roteiro Padrão para Baixa.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_roteiro_padrao_baixa(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_dados_gerais(page)

    # Só dá para imprimir através da consulta
    consultar_roteiro_padrao_baixa(page)
    selecionar_roteiro_padrao_baixa(page)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Roteiro Padrão para Baixa.")
