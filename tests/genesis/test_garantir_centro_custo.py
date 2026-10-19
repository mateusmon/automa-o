import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_cc.consultar_cc_flow import (
    consultar_cc,
)
from flows.corporativo.estrutura_organizacional.cadastro_cc.navegar_para_cc_flow import (
    acessar_cc,
)
from flows.corporativo.estrutura_organizacional.cadastro_cc.preencher_dados_gerais_cc_flow import (
    preencher_dados_gerais_cc,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    selecionar_registro_exato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_centro_custo(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que o Centro de Custo da massa-base exista, sem criar duplicatas."""
    logger.info("Iniciou teste Genesis para garantir Centro de Custo.")

    dados_link = contexto_cliente.dados_usuario("link")
    centro_custo = contexto_cliente.centro_custo()

    login(page, dados_link)
    acessar_cc(page)
    consultar_cc(page, centro_custo)

    if selecionar_registro_exato(page, centro_custo["nome"]):
        logger.info("Centro de Custo da massa-base já existe. Nenhuma criação necessária.")
        logout(page)
        logger.success("Finalizou teste Genesis para garantir Centro de Custo.")
        return

    if not preencher_dados_gerais_cc(page, centro_custo):
        logger.warning("Pulando teste.")
        pytest.skip()

    acessar_cc(page)
    consultar_cc(page, centro_custo)
    assert selecionar_registro_exato(page, centro_custo["nome"]), (
        "Centro de Custo da massa-base não foi encontrado após o cadastro."
    )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Centro de Custo.")
