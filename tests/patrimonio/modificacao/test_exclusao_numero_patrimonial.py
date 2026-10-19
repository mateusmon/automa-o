import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.numero_patrimonial.consulta_numero_patrimonial.consultar_numero_patrimonial_flow import (
    consultar_numero_patrimonial,
)
from flows.patrimonio.modificacao.numero_patrimonial.consulta_numero_patrimonial.selecionar_numero_patrimonial_flow import (
    selecionar_numero_patrimonial,
)
from flows.patrimonio.modificacao.numero_patrimonial.navegar_para_numero_patrimonial_flow import (
    acessar_numero_patrimonial,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_numero_patrimonial(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Modificação do Número Patrimonial.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_numero_patrimonial(page)

    if not consultar_numero_patrimonial(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not selecionar_numero_patrimonial(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Modificação do Número Patrimonial.")
