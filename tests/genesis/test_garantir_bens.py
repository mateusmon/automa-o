from flows.genesis.garantir_bens.criar_bem_flow import criar_bem
from flows.genesis.garantir_bens.verificar_bem_existente_flow import (
    verificar_bem_existente,
)
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante a existência dos Bens informados na massa."""
    logger.info("Iniciou teste Genesis para garantir Bens.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    bens_data = contexto_cliente.bens()

    if not bens_data:
        logger.info("Nenhum bem definido no arquivo yaml. Ignorando fluxo.")
        return

    if isinstance(bens_data, dict):
        bens_data = [bens_data]

    login(page, dados_usuario)

    bens_faltantes = verificar_bem_existente(page, bens_data)

    if not bens_faltantes:
        logger.info("Todos os bens solicitados já existem. Nenhuma criação necessária.")
        logger.success("Finalizou teste Genesis para garantir Bens com sucesso.")
        logout(page)
        return

    criar_bem(page=page, bens_faltantes=bens_faltantes)

    # Pós-validação apenas dos bens cadastrados
    verificacao_pos = verificar_bem_existente(page, bens_faltantes)

    fmt_faltantes = [
        f"Nome Completo: {item['nome']} {item['complemento']}"
        for item in verificacao_pos
    ]

    assert len(verificacao_pos) == 0, (
        f"Os seguintes bens não foram encontrados após o cadastro: {fmt_faltantes}"
    )

    logger.success("Finalizou teste Genesis para garantir Bens com sucesso.")
    logout(page)
