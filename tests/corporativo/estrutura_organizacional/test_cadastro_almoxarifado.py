from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.navegar_para_almoxarifado_flow import (
    acessar_almoxarifado,
)
from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.preencher_dados_gerais_almoxarifado_flow import (
    preencher_dados_gerais_almoxarifado,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_almoxarifado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Almoxarifado.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_cr()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_almoxarifado(page)
    preencher_dados_gerais_almoxarifado(page, almoxarifado, ug)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Almoxarifado.")
