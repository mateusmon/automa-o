from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.intervalo_n_patrimoniais.consultar_intervalo_n_patrimoniais_flow import (
    consultar_intervalo_n_patrimoniais,
)
from flows.patrimonio.auxiliares.intervalo_n_patrimoniais.navegar_para_intervalo_n_patrimoniais_flow import (
    acessar_intervalo_n_patrimoniais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


# O intervalo de números patrimoniais já é criado pelo Genesis, e por isso, somente a consulta é feita.
def test_consulta_intervalo_n_patrimoniais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Intervalo de Nº Patrimoniais.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_intervalo_n_patrimoniais(page)
    consultar_intervalo_n_patrimoniais(page, ug)
    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Intervalo de Nº Patrimoniais.")
