import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.termo_responsabilidade.emissao_termo_responsabilidade.consultar_emissao_termo_responsabilidade.consultar_emissao_termo_responsabilidade_flow import (
    consultar_emissao_termo_responsabilidade,
)
from flows.patrimonio.termo_responsabilidade.emissao_termo_responsabilidade.navegando_para_emissao_termo_responsabilidade_flow import (
    acessar_emissao_termo_responsabilidade,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_emissao_termo_responsabilidade(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Emissão do Termo de Responsabilidade.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_emissao_termo_responsabilidade(page)

    if not consultar_emissao_termo_responsabilidade(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Emissão do Termo de Responsabilidade.")