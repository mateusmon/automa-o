from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcao.consultar_funcao_flow import (
    consultar_funcao,
)
from flows.corporativo.funcionario.cadastro_funcao.navegar_para_funcao_flow import (
    acessar_funcao,
)
from flows.corporativo.funcionario.cadastro_funcao.preencher_dados_gerais_funcao_flow import (
    preencher_dados_gerais_funcao,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    selecionar_registro_exato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_funcao(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que a Função da massa-base exista, sem criar duplicatas."""
    logger.info("Iniciou teste Genesis para garantir Função.")

    dados_link = contexto_cliente.dados_usuario("link")
    funcao = contexto_cliente.funcao()

    login(page, dados_link)
    acessar_funcao(page)
    consultar_funcao(page, funcao)

    if selecionar_registro_exato(page, funcao["nome"]):
        logger.info("Função da massa-base já existe. Nenhuma criação necessária.")
        logout(page)
        logger.success("Finalizou teste Genesis para garantir Função.")
        return

    preencher_dados_gerais_funcao(page, funcao)

    acessar_funcao(page)
    consultar_funcao(page, funcao)
    assert selecionar_registro_exato(page, funcao["nome"]), (
        "Função da massa-base não foi encontrada após o cadastro."
    )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Função.")
