import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_externa.recebimento_transferencia_almoxarifado.navegar_para_recebimento_transferencia_almoxarivado import (
    acessar_recebimento_transferencia_almoxarifado,
)
from flows.almoxarifado.movimentacao_externa.recebimento_transferencia_almoxarifado.receber_transferencia__almoxarifado import (
    efetuar_recebimento_transferencia,
)
from flows.almoxarifado.movimentacao_externa.recebimento_transferencia_almoxarifado.validar_botoes_flow import (
    validar_botoes,
)
from flows.almoxarifado.movimentacao_externa.recebimento_transferencia_almoxarifado.validar_botoes_remover_imprimir_flow import (
    validar_botoes_remover,
)
from flows.shared.retornar_duas_vezes_flow import retornar_duas_vezes
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout



def test_recebimento_transferencia_almoxarifado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou o teste de Recebimento de Transferência entre Almoxarifados.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_por_indice(1)

    login(page, dados_cliente)
    acessar_recebimento_transferencia_almoxarifado(page)

    validar_botoes(page)
    imprimir_relatorio(page, ja_solicitado = True)
    retornar_duas_vezes(page)
    imprimir_relatorio(page, variacao= True)
    retornar_duas_vezes(page)
    validar_botoes_remover(page)

    if not efetuar_recebimento_transferencia(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    
    logger.success("Finalizou o teste de Recebimento de Transferência entre Almoxarifados.")
