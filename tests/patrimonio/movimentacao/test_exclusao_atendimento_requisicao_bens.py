import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.consultar_atendimento_flow import (
    consultar_atendimento,
)
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.navegar_para_atendimento_flow import (
    acessar_atendimento,
)
from flows.patrimonio.movimentacao.atendimento_requisicao_bens.selecionar_atendimento_flow import (
    selecionar_atendimento,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta_atendimento_requisicao_bens(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Atendimento de Requisição de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_padrao()
    bem = contexto_cliente.bem_padrao()
    
    login(page, dados_cliente)

    if not acessar_atendimento(page):
        logger.info("Menu 'Requisição - Atendimento' não disponível para o cliente. Pulando teste.")
        pytest.skip()

    consultar_atendimento(page, ug, bem)

    if not selecionar_atendimento(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Atendimento de Requisição de Bens.")
