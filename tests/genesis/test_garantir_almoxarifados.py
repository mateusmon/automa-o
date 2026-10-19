from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.genesis.garantir_almoxarifados.criar_almoxarifado_flow import (
    criar_almoxarifado,
)
from flows.genesis.garantir_almoxarifados.verificar_almoxarifado_existente_flow import (
    verificar_almoxarifado_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_almoxarifados(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que os Almoxarifados da massa-base existam sem duplicá-los."""
    logger.info("Iniciou teste Genesis para garantir Almoxarifados.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    almoxarifados_data = contexto_cliente.almoxarifados()
    ug = contexto_cliente.ug()

    if not almoxarifados_data:
        logger.info("Nenhum almoxarifado definido no arquivo yaml. Ignorando teste.")
        return

    login(page, dados_usuario)
    almoxarifados_faltantes = verificar_almoxarifado_existente(
        page, ug, almoxarifados_data
    )

    if not almoxarifados_faltantes:
        logger.info(
            "Todos os Almoxarifados da massa-base já existem. Nenhuma criação necessária."
        )
        logout(page)
        logger.success("Finalizou teste Genesis para garantir Almoxarifados.")
        return

    criar_almoxarifado(
        page=page,
        almoxarifados_faltantes=almoxarifados_faltantes,
        sigla_ug=ug["sigla"],
    )

    almoxarifados_restantes = verificar_almoxarifado_existente(
        page, ug, almoxarifados_faltantes
    )
    assert len(almoxarifados_restantes) == 0, (
        f"Os seguintes almoxarifados não foram encontrados após o cadastro: "
        f"{[a['sigla'] for a in almoxarifados_restantes]}"
    )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Almoxarifados com sucesso.")
