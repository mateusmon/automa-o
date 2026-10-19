import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.status_bem.alteracao_status_bem.alterar_status_bem_flow import (
    alterar_status_bem,
)
from flows.patrimonio.modificacao.status_bem.alteracao_status_bem.desfazer_movimento_flow import (
    desfazer_movimento,
)
from flows.patrimonio.modificacao.status_bem.consultar_modificacao_flow import (
    consultar_modificacao,
)
from flows.patrimonio.modificacao.status_bem.navegar_para_status_bem_flow import (
    acessar_status_bem,
)
from flows.patrimonio.modificacao.status_bem.selecionar_modificacao_flow import (
    selecionar_modificacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_status_bem(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Status Bem.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_status_bem(page)
    consultar_modificacao(page, ug)
    
    if not selecionar_modificacao(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_status_bem(page)

    logger.info("Desfazendo mudança.")
    consultar_modificacao(page, ug)
    selecionar_modificacao(page, ug)
    desfazer_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Status Bem.")
