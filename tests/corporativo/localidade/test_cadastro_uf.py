from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_uf.navegar_para_uf_flow import (
    acessar_uf,
)
from flows.corporativo.localidade.cadastro_uf.preencher_dados_gerais_uf_flow import (
    preencher_dados_gerais_uf,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_uf(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de UF - Unidade da Federação.")

    dados_cliente = contexto_cliente.dados_cliente()
    uf = contexto_cliente.uf_cr()

    login(page, dados_cliente)
    acessar_uf(page)
    preencher_dados_gerais_uf(page, uf)
    logout(page)

    logger.success("Finalizou teste de Cadastro de UF - Unidade da Federação.")
