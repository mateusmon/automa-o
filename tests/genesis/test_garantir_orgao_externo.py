from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.genesis.garantir_orgao_externo.criar_orgao_externo_flow import (
    criar_orgao_externo,
)
from flows.genesis.garantir_orgao_externo.verificar_orgao_externo_existente_flow import (
    verificar_orgao_externo_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_orgao_externo(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que os órgãos externos definidos na massa existam sem duplicá-los."""
    logger.info("Iniciou teste Genesis para garantir Órgão Externo.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    orgaos_externos_data = contexto_cliente.orgao_externo()

    if not orgaos_externos_data:
        logger.info("Nenhum órgão externo definido no arquivo yaml. Ignorando fluxo.")
        return

    # Normaliza para lista caso o YAML contenha um único dicionário em vez de lista
    if isinstance(orgaos_externos_data, dict):
        orgaos_externos_data = [orgaos_externos_data]

    login(page, dados_usuario)
    orgaos_faltantes = verificar_orgao_externo_existente(page, orgaos_externos_data)

    if not orgaos_faltantes:
        logger.info(
            "Todos os órgãos externos da massa-base já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir Órgão Externo.")
        logout(page)
        return

    criar_orgao_externo(
        page=page,
        orgaos_faltantes=orgaos_faltantes,
    )

    orgaos_restantes = verificar_orgao_externo_existente(page, orgaos_faltantes)
    assert len(orgaos_restantes) == 0, (
        f"Os seguintes órgãos externos não foram encontrados após o cadastro: "
        f"{[o['nome'] for o in orgaos_restantes]}"
    )

    logger.success("Finalizou teste Genesis para garantir Órgão Externo com sucesso.")
    logout(page)
