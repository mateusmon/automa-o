import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.atender_transferencia import (
    atender_requisicao,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.escolher_lote_flow import (
    escolher_lote,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.navegar_para_atendimento_transferencia_almoxarifado_flow import (
    acessar_atendimento_transferencia_almoxarifado,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.selecionar_almoxarifado_flow import (
    selecionar_almoxarifado,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.selecionar_transferencia_para_atender_flow import (
    selecionar_transferencia,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.verificar_item_transferencia_flow import (
    verificar_item_transferencia,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_atendimento_transferencia_almoxarifados(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Atendimento de Transferência entre Almoxarifados.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    almoxarifado_solicitante = contexto_cliente.almoxarifado_por_indice(1)
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_atendimento_transferencia_almoxarifado(page)
    selecionar_almoxarifado(page, almoxarifado)

    if not selecionar_transferencia(page, almoxarifado_solicitante):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not verificar_item_transferencia(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    escolher_lote(page)
    atender_requisicao(page, material)

    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Atendimento de Transferência entre Almoxarifados.")
