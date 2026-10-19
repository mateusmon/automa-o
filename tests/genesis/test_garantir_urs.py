from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.estrutura_organizacional.cadastro_ur.consultar_ur_flow import (
    consultar_ur,
)
from flows.corporativo.estrutura_organizacional.cadastro_ur.navegar_para_ur_flow import (
    acessar_ur,
)
from flows.corporativo.estrutura_organizacional.cadastro_ur.preencher_dados_basicos_ur_flow import (
    preencher_dados_basicos_ur,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    selecionar_registro_exato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_urs(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que as Unidades de Requisição da massa-base existam, criando somente as ausentes."""
    logger.info("Iniciou teste Genesis para garantir Unidades de Requisição.")

    dados_link = contexto_cliente.dados_usuario("link")
    urs = contexto_cliente.urs()

    login(page, dados_link)
    acessar_ur(page)

    total = len(urs)
    logger.info("Foi encontrado um total de {} unidades de requisição no blueprint.", total)

    for atual, ur in enumerate(urs, start=1):
        nome = ur["nome"]

        logger.info("Unidade de requisição {}/{}: '{}'.", atual, total, nome)

        consultar_ur(page, ur)

        if selecionar_registro_exato(page, nome):
            logger.info("Unidade de requisição '{}' já existe. Nenhuma ação necessária.", nome)
            continue

        acessar_ur(page)
        preencher_dados_basicos_ur(page, ur)

        acessar_ur(page)
        consultar_ur(page, ur)
        assert selecionar_registro_exato(page, nome), (
            f"Unidade de requisição '{nome}' não foi encontrada após o cadastro."
        )

        logger.success("Unidade de requisição '{}' criada com sucesso.", nome)

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Unidades de Requisição.")