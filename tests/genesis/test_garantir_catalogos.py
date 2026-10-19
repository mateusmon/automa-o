from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.genesis.garantir_catalogos.criar_catalogo_flow import criar_catalogo
from flows.genesis.garantir_catalogos.verificar_catalogo_existente_flow import (
    verificar_catalogo_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_catalogos(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante a criação dos catálogos configurados no blueprint para cada almoxarifado."""
    logger.info("Iniciou teste Genesis para garantir Catálogos.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    catalogo_data = contexto_cliente.catalogo()
    almoxarifados_data = contexto_cliente.almoxarifados()
    urs_data = contexto_cliente.urs()

    if not catalogo_data or not almoxarifados_data or not urs_data:
        logger.info(
            "Massa de dados incompleta no YAML para Catálogos. Ignorando fluxo."
        )
        return

    if isinstance(almoxarifados_data, dict):
        almoxarifados_data = [almoxarifados_data]
    if isinstance(urs_data, dict):
        urs_data = [urs_data]

    login(page, dados_usuario)

    catalogos_faltantes = verificar_catalogo_existente(
        page, almoxarifados_data, catalogo_data
    )

    if not catalogos_faltantes:
        logger.info(
            "Todos os catálogos para os almoxarifados já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir Catálogos com sucesso.")
        logout(page)
        return

    criar_catalogo(
        page=page,
        catalogos_faltantes=catalogos_faltantes,
        catalogo_data=catalogo_data,
        urs_data=urs_data,
    )

    # Re-verifica apenas os catálogos/almoxarifados que precisavam ser criados
    verificacao_pos = verificar_catalogo_existente(
        page, catalogos_faltantes, catalogo_data
    )

    fmt_faltantes = [
        f"Almoxarifado: {alm['sigla']} (Catálogo: {catalogo_data.get('nome')})"
        for alm in verificacao_pos
    ]

    assert len(verificacao_pos) == 0, (
        f"Os seguintes catálogos não foram validados após o cadastro: {fmt_faltantes}"
    )

    logger.success("Finalizou teste Genesis para garantir Catálogos com sucesso.")
    logout(page)
