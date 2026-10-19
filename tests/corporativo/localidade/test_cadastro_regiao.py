from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_regiao.navegar_para_regiao_flow import (
    acessar_regiao,
)
from flows.corporativo.localidade.cadastro_regiao.preencher_dados_gerais_regiao_flow import (
    preencher_dados_gerais_regiao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_regiao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Região.")

    dados_cliente = contexto_cliente.dados_cliente()
    regiao = contexto_cliente.regiao_cr()

    login(page, dados_cliente)
    acessar_regiao(page)
    preencher_dados_gerais_regiao(page, regiao)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Região.")
