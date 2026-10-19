import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.auxiliares.definicao_caracteristicas.alteracao_definicao_caracteristica.alterar_caracteristica_flow import (
    alterar_caracteristica,
)
from flows.almoxarifado.auxiliares.definicao_caracteristicas.consulta_definicao_caracteristica.consultar_definicao_caracteristica_flow import (
    consultar_definicao_caracteristica,
)
from flows.almoxarifado.auxiliares.definicao_caracteristicas.navegar_pagina_definicao_caracteristica_flow import (
    acessar_definicao_caracteristicas,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_almoxarifado_alteracao_definicao_caracteristica(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Definição das Características.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)

    if not acessar_definicao_caracteristicas(page):
        logger.warning("Submódulo 'Definição das Características' não disponível para este cliente. Pulando teste.")
        pytest.skip()

    if not consultar_definicao_caracteristica(page, "MARCA AUTOMATIZADA"):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_caracteristica(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Definição das Características.")