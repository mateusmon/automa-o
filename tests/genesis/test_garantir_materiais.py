from flows.genesis.garantir_materiais.criar_material_flow import (
    criar_material,
)
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.material.cadastro_material_consumo.navegar_para_material_consumo_flow import (
    acessar_material_consumo,
)
from flows.genesis.garantir_materiais.verificar_material_existente_flow import (
    verificar_material_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que os materiais definidos no blueprint existam sem duplicá-los."""
    logger.info("Iniciou teste Genesis para garantir Materiais de Consumo.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    try:
        materiais_data = contexto_cliente.materiais()
    except ValueError:
        materiais_data = []

    if not materiais_data:
        logger.info("Nenhum material definido no arquivo yaml. Ignorando fluxo.")
        return

    login(page, dados_usuario)
    acessar_material_consumo(page)
    materiais_faltantes = verificar_material_existente(page, materiais_data)

    if not materiais_faltantes:
        logger.info(
            "Todos os materiais da massa-base já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir Materiais.")
        logout(page)
        return

    criar_material(
        page=page,
        materiais_faltantes=materiais_faltantes,
    )

    acessar_material_consumo(page)
    materiais_restantes = verificar_material_existente(page, materiais_faltantes)
    assert len(materiais_restantes) == 0, (
        f"Os seguintes materiais não foram encontrados após o cadastro: "
        f"{[m['nome'] for m in materiais_restantes]}"
    )

    logger.success("Finalizou teste Genesis para garantir Materiais com sucesso.")
    logout(page)
