import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_uf.consultar_uf_flow import (
    consultar_uf,
)
from flows.corporativo.localidade.cadastro_uf.navegar_para_uf_flow import (
    acessar_uf,
)
from flows.corporativo.localidade.cadastro_uf.selecionar_uf_flow import (
    selecionar_uf,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_uf(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de UF - Unidade da Federação.")

    dados_cliente = contexto_cliente.dados_cliente()
    uf = contexto_cliente.uf_cr()

    login(page, dados_cliente)
    acessar_uf(page)
    consultar_uf(page, uf)

    if not selecionar_uf(page, uf):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)

    logger.success("Finalizou teste de Exclusão de UF - Unidade da Federação.")
