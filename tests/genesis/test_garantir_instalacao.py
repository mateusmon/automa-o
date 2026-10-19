from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_instalacao.consultar_instalacao_flow import (
    consultar_instalacao,
)
from flows.corporativo.localidade.cadastro_instalacao.navegar_para_instalacao_flow import (
    acessar_instalacao,
)
from flows.corporativo.localidade.cadastro_instalacao.preencher_dados_basicos_instalacao_flow import (
    preencher_dados_basicos_instalacao,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    selecionar_registro_exato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_instalacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que a Instalação da massa-base exista, sem criar duplicatas."""
    logger.info("Iniciou teste Genesis para garantir Instalação.")

    dados_link = contexto_cliente.dados_usuario("link")
    instalacao = contexto_cliente.instalacao()

    login(page, dados_link)
    acessar_instalacao(page)
    consultar_instalacao(page, instalacao)

    if selecionar_registro_exato(page, instalacao["nome"]):
        logger.info("Instalação da massa-base já existe. Nenhuma criação necessária.")
        logout(page)
        logger.success("Finalizou teste Genesis para garantir Instalação.")
        return

    acessar_instalacao(page)
    preencher_dados_basicos_instalacao(page, instalacao)

    acessar_instalacao(page)
    consultar_instalacao(page, instalacao)
    assert selecionar_registro_exato(page, instalacao["nome"]), (
        "Instalação da massa-base não foi encontrada após o cadastro."
    )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Instalação.")
