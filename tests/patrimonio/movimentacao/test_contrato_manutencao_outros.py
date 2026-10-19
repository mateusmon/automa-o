import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.contrato_manutencao.navegar_para_contrato_manutencao_flow import (
    acessar_contrato_manutencao,
)
from flows.patrimonio.movimentacao.contrato_manutencao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.contrato_manutencao.preencher_itens_flow import (
    preencher_itens,
)
from flows.patrimonio.shared.confirmar_e_pular_impressao_flow import confirmar
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from flows.shared.retornar_duas_vezes_flow import retornar_duas_vezes


def test_contrato_manutencao_outros(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Contrato de Manutenção de Outros ou Diversos.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    fornecedor = contexto_cliente.fornecedor_padrao()
    bem = contexto_cliente.bem_padrao()
    
    login(page, dados_cliente)
    acessar_contrato_manutencao(page)
    preencher_dados_gerais(page, ug, fornecedor, "OUTROS OU DIVERSOS")
    
    if not preencher_itens(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    confirmar(page)
    imprimir_relatorio(page)
    retornar_duas_vezes(page)

    logger.info("Desfazendo mudança.")
    excluir_movimento(page)
    logout(page)

    logger.success("Finalizou teste de Contrato de Manutenção de Outros ou Diversos.")
