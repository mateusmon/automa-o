from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_unidade_medida.consultar_unidade_medida_flow import (
    consultar_unidade_medida,
)
from flows.corporativo.material.cadastro_unidade_medida.navegar_para_unidade_medida_flow import (
    acessar_unidade_medida,
)
from flows.corporativo.material.cadastro_unidade_medida.preencher_dados_gerais_unidade_medida_flow import (
    preencher_dados_gerais_unidade_medida,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    selecionar_registro_exato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_unidade_medida(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    """Garante que a Unidade de Medida da massa-base exista sem duplicá-la."""
    logger.info("Iniciou teste Genesis para garantir Unidade de Medida.")

    dados_teste = contexto_cliente.dados_usuario("teste")
    unidade_medida = contexto_cliente.unidade_medida()

    login(page, dados_teste)
    acessar_unidade_medida(page)
    consultar_unidade_medida(page, unidade_medida)

    if selecionar_registro_exato(page, unidade_medida["sigla"]):
        logger.info(
            "Unidade de Medida da massa-base já existe. Nenhuma criação necessária."
        )
        logout(page)
        logger.success("Finalizou teste Genesis para garantir Unidade de Medida.")
        return

    preencher_dados_gerais_unidade_medida(page, unidade_medida)

    acessar_unidade_medida(page)
    consultar_unidade_medida(page, unidade_medida)
    assert selecionar_registro_exato(page, unidade_medida["sigla"]), (
        "Unidade de Medida da massa-base não foi encontrada após o cadastro."
    )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Unidade de Medida.")
