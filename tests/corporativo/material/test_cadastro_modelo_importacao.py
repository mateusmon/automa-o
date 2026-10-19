import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_modelo_importacao.consultar_caracteristicas_flow import (
    consultar_caracteristicas,
)
from flows.corporativo.material.cadastro_modelo_importacao.navegar_para_modelo_importacao_flow import (
    acessar_modelo_importacao,
)
from flows.corporativo.material.cadastro_modelo_importacao.preencher_dados_gerais_modelo_importacao_flow import (
    preencher_dados_gerais_modelo_importacao,
)
from flows.corporativo.material.cadastro_modelo_importacao.selecionar_caracteristicas_flow import (
    selecionar_caracteristicas,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_modelo_importacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Modelo de Importação.")

    dados_cliente = contexto_cliente.dados_cliente()
    modelo = contexto_cliente.modelo_importacao_cr()

    login(page, dados_cliente)
    acessar_modelo_importacao(page)
    preencher_dados_gerais_modelo_importacao(page, modelo)
    consultar_caracteristicas(page)

    if not selecionar_caracteristicas(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Modelo de Importação.")
