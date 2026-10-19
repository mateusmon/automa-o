from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_unidade_medida.navegar_para_unidade_medida_flow import (
    acessar_unidade_medida,
)
from flows.corporativo.material.cadastro_unidade_medida.preencher_dados_gerais_unidade_medida_flow import (
    preencher_dados_gerais_unidade_medida,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_unidade_medida(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Unidade de Medida.")

    dados_cliente = contexto_cliente.dados_cliente()
    unidade_medida = contexto_cliente.unidade_medida_cr()

    login(page, dados_cliente)
    acessar_unidade_medida(page)
    preencher_dados_gerais_unidade_medida(page, unidade_medida)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Unidade de Medida.")
