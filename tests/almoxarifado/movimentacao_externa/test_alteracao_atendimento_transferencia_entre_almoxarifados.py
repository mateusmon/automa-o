import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.altera_atendimento_transferencia_entre_almoxarifados.alterar_atendimento_transferencia_entre_almoxarifados_flow import (
    alterar_atendimento_transferencia_entre_almoxarifados,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.consulta.consultar_atendimento_transferencia_almoxarifados_flow import (
    consultar_atendimento,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.navegar_para_atendimento_transferencia_almoxarifado_flow import (
    acessar_atendimento_transferencia_almoxarifado,
)
from flows.almoxarifado.movimentacao_externa.atendimento_transferencia_almoxarifado.selecionar_transferencia_flow import (
    selecionar_transferencia,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_atendimento_entre_almoxarifados(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Atendimento de Transferência entre Almoxarifados.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    almoxarifado_solicitante = contexto_cliente.almoxarifado_por_indice(1)
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_atendimento_transferencia_almoxarifado(page)
    consultar_atendimento(page, almoxarifado, almoxarifado_solicitante, material)

    if not selecionar_transferencia(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not alterar_atendimento_transferencia_entre_almoxarifados(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Atendimento de Transferência entre Almoxarifados.")
