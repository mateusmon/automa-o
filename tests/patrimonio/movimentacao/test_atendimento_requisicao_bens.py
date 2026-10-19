import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.escolher_bens_flow import (
    escolher_bens,
)
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.navegar_para_atendimento_flow import (
    acessar_atendimento,
)
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.preencher_demais_dados_flow import (
    preencher_demais_dados,
)
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.selecionar_requisicao_flow import (
    selecionar_requisicao,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_atendimento_requisicao_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Atendimento de Requisição de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_padrao()
    bem = contexto_cliente.bem_padrao()
    
    login(page, dados_cliente)

    if not acessar_atendimento(page):
            logger.info("Menu 'Requisição - Atendimento' não disponível para o cliente. Pulando teste.")
            pytest.skip()
            
    preencher_dados_gerais(page, ug)

    if not selecionar_requisicao(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_demais_dados(page)

    if not escolher_bens(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()
        
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Atendimento de Requisição de Bens.")
