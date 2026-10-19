from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.nivel_estoque.esperar_visualizacao_flow import (
    esperar_visualizacao,
)
from flows.almoxarifado.gestao_de_compras.nivel_estoque.navegar_para_nivel_estoque_flow import (
    acessar_nivel_estoque,
)
from flows.almoxarifado.gestao_de_compras.nivel_estoque.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_nivel_estoque(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Nível de Estoque.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado_data = contexto_cliente.almoxarifado_padrao()
    
    login(page, dados_cliente)
    acessar_nivel_estoque(page)
    preencher_dados_gerais(page, almoxarifado_data)
    esperar_visualizacao(page, 5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Nível de Estoque.")
