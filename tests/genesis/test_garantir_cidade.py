from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_cidade.consultar_cidade_flow import (
    consultar_cidade,
)
from flows.corporativo.localidade.cadastro_cidade.navegar_para_cidade_flow import (
    acessar_cidade,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    verificar_cidade_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_cidade(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Valida a Cidade comum existente, sem cadastrá-la nem corrigi-la."""
    logger.info("Iniciou teste Genesis para validar Cidade.")

    dados_link = contexto_cliente.dados_usuario("link")
    cidade = contexto_cliente.cidade()

    login(page, dados_link)
    acessar_cidade(page)
    consultar_cidade(page, cidade)

    assert verificar_cidade_existente(page, cidade["nome"]), (
        "Cidade comum não encontrada com nem sem acento; o piloto não a cadastra."
    )

    logout(page)
    logger.success("Finalizou teste Genesis para validar Cidade.")
