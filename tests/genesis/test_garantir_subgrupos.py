import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.genesis.garantir_subgrupos.criar_subgrupo_flow import (
    criar_subgrupo,
)
from flows.genesis.garantir_subgrupos.verificar_subgrupo_existente_flow import (
    verificar_subgrupo_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_subgrupos(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que os subgrupos definidos nos grupos da massa existam sem duplicá-los."""
    logger.info("Iniciou teste Genesis para garantir Subgrupos.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    grupos_data = contexto_cliente.grupos()

    if not grupos_data:
        logger.info(
            "Nenhum grupo ou subgrupo definido no arquivo yaml. Ignorando fluxo."
        )
        return

    # Normaliza dicionário único para lista, se necessário
    if isinstance(grupos_data, dict):
        grupos_data = [grupos_data]

    login(page, dados_usuario)
    subgrupos_faltantes = verificar_subgrupo_existente(page, grupos_data)

    if subgrupos_faltantes is None:
        logger.info("Pulando teste.")
        pytest.skip()

    if not subgrupos_faltantes:
        logger.info(
            "Todos os subgrupos da massa-base já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir Subgrupos.")
        logout(page)
        return

    criar_subgrupo(
        page=page,
        subgrupos_faltantes=subgrupos_faltantes,
    )

    subgrupos_restantes = verificar_subgrupo_existente(
        page, [{"subgrupos": subgrupos_faltantes}]
    )
    assert len(subgrupos_restantes) == 0, (
        f"Os seguintes subgrupos não foram encontrados após o cadastro: "
        f"{[s['nome'] for s in subgrupos_restantes]}"
    )

    logger.success("Finalizou teste Genesis para garantir Subgrupos com sucesso.")
    logout(page)
