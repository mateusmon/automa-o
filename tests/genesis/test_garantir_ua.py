from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ua.consultar_ua_flow import (
    consultar_ua,
)
from flows.corporativo.estrutura_organizacional.cadastro_ua.navegar_para_ua_flow import (
    acessar_ua,
)
from flows.corporativo.estrutura_organizacional.cadastro_ua.preencher_dados_gerais_ua_flow import (
    preencher_dados_gerais_ua,
)
from flows.corporativo.estrutura_organizacional.cadastro_ua.verificar_ua_existente_flow import (
    verificar_ua_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_ua(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que a Unidade Administrativa da massa-base exista, sem criar duplicatas."""
    logger.info("Iniciou teste Genesis para garantir Unidade Administrativa.")

    dados_link = contexto_cliente.dados_usuario("link")
    ua = contexto_cliente.ua()
    ug = contexto_cliente.ug()

    login(page, dados_link)
    acessar_ua(page)
    consultar_ua(page, ua)

    if verificar_ua_existente(page):
        logger.info("Unidade Administrativa da massa-base já existe. Nenhuma criação necessária.")
        logout(page)
        logger.success("Finalizou teste Genesis para garantir Unidade Administrativa.")
        return

    preencher_dados_gerais_ua(page, ua, ug)

    acessar_ua(page)
    consultar_ua(page, ua)
    assert verificar_ua_existente(page), (
        "Unidade Administrativa da massa-base não foi encontrada após o cadastro."
    )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Unidade Administrativa.")
