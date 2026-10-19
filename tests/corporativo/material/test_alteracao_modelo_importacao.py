import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_modelo_importacao.alterar_modelo_importacao_flow import (
    alterar_modelo_importacao,
)
from flows.corporativo.material.cadastro_modelo_importacao.consultar_modelo_importacao_flow import (
    consultar_modelo_importacao,
)
from flows.corporativo.material.cadastro_modelo_importacao.navegar_para_modelo_importacao_flow import (
    acessar_modelo_importacao,
)
from flows.corporativo.material.cadastro_modelo_importacao.selecionar_modelo_importacao_flow import (
    selecionar_modelo_importacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_modelo_importacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Modelo de Importação.")

    dados_cliente = contexto_cliente.dados_cliente()
    modelo = contexto_cliente.modelo_importacao_cr()

    login(page, dados_cliente)
    acessar_modelo_importacao(page)
    consultar_modelo_importacao(page, modelo)

    if not selecionar_modelo_importacao(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_modelo_importacao(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Modelo de Importação.")
