import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.caracteristica_bem.consultar_definicao_caracteristica_flow import (
    consultar_definicao_caracteristica,
)
from flows.corporativo.caracteristica_bem.navegar_para_definicao_caracteristica_flow import (
    acessar_definicao_caracteristica,
)
from flows.corporativo.caracteristica_bem.selecionar_definicao_caracteristica_flow import (
    selecionar_definicao_caracteristica,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_corporativo_exclusao_definicao_caracteristica(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Definição da Característica.")

    dados_cliente = contexto_cliente.dados_cliente()
    caracteristica = contexto_cliente.caracteristica_bem_cr()

    login(page, dados_cliente)
    acessar_definicao_caracteristica(page)
    consultar_definicao_caracteristica(page, caracteristica)

    if not selecionar_definicao_caracteristica(page, caracteristica):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Definição da Característica.")
