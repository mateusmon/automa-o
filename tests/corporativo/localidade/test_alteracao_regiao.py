import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_regiao.alterar_regiao_flow import (
    alterar_regiao,
)
from flows.corporativo.localidade.cadastro_regiao.consultar_regiao_flow import (
    consultar_regiao,
)
from flows.corporativo.localidade.cadastro_regiao.navegar_para_regiao_flow import (
    acessar_regiao,
)
from flows.corporativo.localidade.cadastro_regiao.selecionar_regiao_flow import (
    selecionar_regiao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_regiao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Região.")

    dados_cliente = contexto_cliente.dados_cliente()
    regiao = contexto_cliente.regiao_cr()

    login(page, dados_cliente)
    acessar_regiao(page)
    consultar_regiao(page, regiao)

    if not selecionar_regiao(page, regiao):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_regiao(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Região.")
