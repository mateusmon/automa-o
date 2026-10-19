from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.genesis.garantir_enderecos_material.criar_endereco_material_flow import (
    criar_endereco_material,
)
from flows.genesis.garantir_enderecos_material.verificar_endereco_material_existente_flow import (
    verificar_endereco_material_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_enderecos_material(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    """Garante que os endereços de estoque definidos no blueprint existam para os almoxarifados."""
    logger.info("Iniciou teste Genesis para garantir Endereços de Estoque.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    almoxarifados_data = contexto_cliente.almoxarifados()
    enderecos_data = contexto_cliente.enderecos_material()

    if not almoxarifados_data:
        logger.info("Nenhum almoxarifado definido no arquivo yaml. Ignorando fluxo.")
        return

    if not enderecos_data:
        logger.info(
            "Nenhum endereço de material definido no arquivo yaml. Ignorando fluxo."
        )
        return

    # Normaliza para lista caso venha como dicionário único
    if isinstance(almoxarifados_data, dict):
        almoxarifados_data = [almoxarifados_data]
    if isinstance(enderecos_data, dict):
        enderecos_data = [enderecos_data]

    login(page, dados_usuario)
    enderecos_faltantes = verificar_endereco_material_existente(
        page, almoxarifados_data, enderecos_data
    )

    if not enderecos_faltantes:
        logger.info(
            "Todos os endereços de estoque da massa-base já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir Endereços de Estoque.")
        logout(page)
        return

    criar_endereco_material(
        page=page,
        enderecos_faltantes=enderecos_faltantes,
    )

    # Re-verifica apenas os itens que precisavam ser criados
    verificacao_pos_criacao = []
    for item in enderecos_faltantes:
        res = verificar_endereco_material_existente(
            page, [item["almoxarifado"]], [item["endereco"]]
        )
        verificacao_pos_criacao.extend(res)

    # Extrai as descrições formatadas para evitar o conflito de aspas na f-string
    itens_faltantes_fmt = [
        f"{it['almoxarifado']['sigla']}: {it['endereco']['descricao']}"
        for it in verificacao_pos_criacao
    ]

    assert len(verificacao_pos_criacao) == 0, (
        f"Os seguintes endereços de material não foram encontrados após o cadastro: {itens_faltantes_fmt}"
    )

    logger.success(
        "Finalizou teste Genesis para garantir Endereços de Estoque com sucesso."
    )
    logout(page)
