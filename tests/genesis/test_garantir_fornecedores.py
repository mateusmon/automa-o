from flows.genesis.garantir_fornecedores.criar_fornecedor_flow import (
    criar_fornecedor,
)
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.entidade_externa.cadastro_fornecedor.navegar_para_fornecedor_flow import (
    acessar_fornecedor,
)
from flows.genesis.garantir_fornecedores.verificar_fornecedor_existente_flow import (
    verificar_fornecedor_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_fornecedores(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que os fornecedores definidos no blueprint existam sem duplicá-los."""
    logger.info("Iniciou teste Genesis para garantir Fornecedores.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    fornecedores_data = contexto_cliente.fornecedores()

    if not fornecedores_data:
        logger.info("Nenhum fornecedor definido no arquivo yaml. Ignorando fluxo.")
        return

    login(page, dados_usuario)
    acessar_fornecedor(page)
    fornecedores_faltantes = verificar_fornecedor_existente(page, fornecedores_data)

    if not fornecedores_faltantes:
        logger.info(
            "Todos os fornecedores da massa-base já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir Fornecedores.")
        return

    criar_fornecedor(
        page=page,
        fornecedores_faltantes=fornecedores_faltantes,
    )

    fornecedores_restantes = verificar_fornecedor_existente(
        page, fornecedores_faltantes
    )
    assert len(fornecedores_restantes) == 0, (
        f"Os seguintes fornecedores não foram encontrados após o cadastro: "
        f"{[f['nome'] for f in fornecedores_restantes]}"
    )

    logger.success("Finalizou teste Genesis para garantir Fornecedores com sucesso.")
    logout(page)
