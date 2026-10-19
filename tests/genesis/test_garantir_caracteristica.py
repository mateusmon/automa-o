from flows.genesis.garantir_caracteristica.criar_caracteristica_flow import (
    criar_caracteristica,
)
from flows.genesis.garantir_caracteristica.verificar_caracteristica_existente_flow import (
    verificar_caracteristica_existente,
)
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_caracteristica(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que o Bem possua uma característica relacionada."""
    logger.info("Iniciou teste Genesis para garantir Característica do Bem.")

    dados_usuario = contexto_cliente.dados_usuario("teste")

    login(page, dados_usuario)

    tem_caracteristica = verificar_caracteristica_existente(page)

    if tem_caracteristica:
        logger.info("Bem já possui característica associada. Nenhuma ação necessária.")
        logger.success(
            "Finalizou teste Genesis para garantir Característica com sucesso."
        )
        logout(page)
        return

    logger.info("Nenhuma característica encontrada no Bem. Iniciando associação...")
    criar_caracteristica(page)

    # Re-verifica a existência no DOM para validar se o cadastro persistiu
    validacao_pos = verificar_caracteristica_existente(page)

    assert validacao_pos is True, (
        "Falha ao validar o relacionamento da característica com o Bem após a criação."
    )

    logger.success("Finalizou teste Genesis para garantir Característica com sucesso.")
    logout(page)
