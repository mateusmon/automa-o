import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_instalacao.consultar_instalacao_flow import (
    consultar_instalacao,
)
from flows.corporativo.localidade.cadastro_instalacao.navegar_para_instalacao_flow import (
    acessar_instalacao,
)
from flows.corporativo.localidade.cadastro_instalacao.selecionar_instalacao_flow import (
    selecionar_instalacao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_instalacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Instalação.")

    dados_cliente = contexto_cliente.dados_cliente()
    instalacao = contexto_cliente.instalacao_cr()

    login(page, dados_cliente)
    acessar_instalacao(page)
    consultar_instalacao(page, instalacao)

    if not selecionar_instalacao(page, instalacao):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Instalação.")
