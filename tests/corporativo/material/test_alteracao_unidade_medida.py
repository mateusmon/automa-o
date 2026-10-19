import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_unidade_medida.alterar_unidade_medida_flow import (
    alterar_unidade_medida,
)
from flows.corporativo.material.cadastro_unidade_medida.consultar_unidade_medida_flow import (
    consultar_unidade_medida,
)
from flows.corporativo.material.cadastro_unidade_medida.navegar_para_unidade_medida_flow import (
    acessar_unidade_medida,
)
from flows.corporativo.material.cadastro_unidade_medida.selecionar_unidade_medida_flow import (
    selecionar_unidade_medida,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_unidade_medida(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Unidade de Medida.")

    dados_cliente = contexto_cliente.dados_cliente()
    unidade_medida = contexto_cliente.unidade_medida_cr()

    login(page, dados_cliente)
    acessar_unidade_medida(page)
    consultar_unidade_medida(page, unidade_medida)

    if not selecionar_unidade_medida(page, unidade_medida):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_unidade_medida(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Unidade de Medida.")
