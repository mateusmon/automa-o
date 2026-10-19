import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.contrato_manutencao.consultar_contratos_flow import (
    consultar_contratos,
)
from flows.patrimonio.movimentacao.contrato_manutencao.navegar_para_contrato_manutencao_flow import (
    acessar_contrato_manutencao,
)
from flows.patrimonio.movimentacao.contrato_manutencao.selecionar_contrato_flow import (
    selecionar_contrato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_contrato_manutencao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de Contrato de Manutenção.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    
    login(page, dados_cliente)
    acessar_contrato_manutencao(page)
    consultar_contratos(page, ug)

    if not selecionar_contrato(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(5_000)
    logout(page)
    
    logger.success("Finalizou teste de Consulta de Contrato de Manutenção.")
