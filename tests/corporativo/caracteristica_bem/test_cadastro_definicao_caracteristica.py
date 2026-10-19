from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.caracteristica_bem.navegar_para_definicao_caracteristica_flow import (
    acessar_definicao_caracteristica,
)
from flows.corporativo.caracteristica_bem.preencher_dados_gerais_definicao_caracteristica_flow import (
    preencher_dados_gerais_definicao_caracteristica,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_definicao_caracteristica(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Definição da Característica.")

    dados_cliente = contexto_cliente.dados_cliente()
    caracteristica = contexto_cliente.caracteristica_bem_cr()

    login(page, dados_cliente)
    acessar_definicao_caracteristica(page)
    preencher_dados_gerais_definicao_caracteristica(page, caracteristica)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Definição da Característica.")
