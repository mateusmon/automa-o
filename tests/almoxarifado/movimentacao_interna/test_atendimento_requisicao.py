import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.atender_requisicao_flow import (
    atender_requisicao,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.escolher_lote_flow import (
    escolher_lote,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.navegar_para_atendimento_requisicao_flow import (
    acessar_atendimento_requisicao,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.preencher_observacao_flow import (
    preencher_observacao,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.selecionar_almoxarifado_flow import (
    selecionar_almoxarifado,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.selecionar_requisicao_flow import (
    selecionar_requisicao,
)
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.verificar_item_requisicao_flow import (
    verificar_item_requisicao,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_atendimento_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Atendimento de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ur = contexto_cliente.ur_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_atendimento_requisicao(page)
    selecionar_almoxarifado(page, almoxarifado)
        
    if not selecionar_requisicao(page, ur):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not verificar_item_requisicao(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    escolher_lote(page)
    preencher_observacao(page)

    # data de inclusão posterior ao mês aberto, não existe solução além do skip
    if not atender_requisicao(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page, timeout_geracao=250_000)
    logout(page)
    
    logger.success("Finalizou teste de Atendimento de Requisição.")
