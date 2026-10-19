import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_externa.recebimento_transferencia_almoxarifado.consulta_recebimento.consultar_recebimento_transferencia_entre_almoxarifados_flow import (
    consultar_recebimento,
)
from flows.almoxarifado.movimentacao_externa.recebimento_transferencia_almoxarifado.consulta_recebimento.selecionar_recebimento_flow import (
    selecionar_recebimento,
)
from flows.almoxarifado.movimentacao_externa.recebimento_transferencia_almoxarifado.navegar_para_recebimento_transferencia_almoxarivado import (
    acessar_recebimento_transferencia_almoxarifado,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_recebimento_transferencia_entre_almoxarifados(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão do Recebimento de Transferência entre Almoxarifados.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()

    login(page, dados_cliente)
    acessar_recebimento_transferencia_almoxarifado(page)
    consultar_recebimento(page, almoxarifado)

    if not selecionar_recebimento(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão do Recebimento de Transferênica entre Almoxarifados.")
