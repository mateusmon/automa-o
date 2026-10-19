import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.modificacao_responsavel_local.consulta_modificacao.consultar_moficação_flow import (
    consultar_modificacao,
)
from flows.patrimonio.modificacao.modificacao_responsavel_local.consulta_modificacao.selecionar_modificacao_flow import (
    selecionar_modificacao,
)
from flows.patrimonio.modificacao.modificacao_responsavel_local.navegar_para_modificacao_responsavel_local_flow import (
    acessar_modificacao_responsavel_local,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_modificacao_responsavel_local(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Modificação de Responsável do Local.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ua = contexto_cliente.ua()

    login(page, dados_cliente)
    acessar_modificacao_responsavel_local(page)
    consultar_modificacao(page, ug, ua)

    if not selecionar_modificacao(page, ua):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Modificação de Responsável do Local.")
