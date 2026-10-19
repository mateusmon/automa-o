from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.intervalo_n_patrimoniais.alterar_intervalo_n_patrimoniais_flow import (
    alterar_intervalo_n_patrimoniais,
)
from flows.patrimonio.auxiliares.intervalo_n_patrimoniais.consultar_intervalo_n_patrimoniais_flow import (
    consultar_intervalo_n_patrimoniais,
)
from flows.patrimonio.auxiliares.intervalo_n_patrimoniais.navegar_para_intervalo_n_patrimoniais_flow import (
    acessar_intervalo_n_patrimoniais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_intervalo_n_patrimoniais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Intervalo de Nº Patrimoniais.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_intervalo_n_patrimoniais(page)
    consultar_intervalo_n_patrimoniais(page, ug)
    alterar_intervalo_n_patrimoniais(page)

    logger.info("Desfazendo alteração de Intervalo de Nº Patrimoniais.")
    consultar_intervalo_n_patrimoniais(page, ug)
    alterar_intervalo_n_patrimoniais(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Intervalo de Nº Patrimoniais.")
