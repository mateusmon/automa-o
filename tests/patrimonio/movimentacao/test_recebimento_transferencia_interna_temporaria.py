import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.recebimento_transferecia_interna.consultar_transferencia_flow import (
    consultar_transferencia,
)
from flows.patrimonio.movimentacao.recebimento_transferecia_interna.efetuar_recebimento_flow import (
    efetuar_recebimento,
)
from flows.patrimonio.movimentacao.recebimento_transferecia_interna.navegar_para_recebimento_transferencia_interna_flow import (
    acessar_recebimento_transferencia_interna,
)
from flows.patrimonio.movimentacao.recebimento_transferecia_interna.selecionar_transferencia_flow import (
    selecionar_transferencia,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_recebimento_transferencia_interna_temporaria(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Recebimento de Transferência Interna Temporária.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ul = contexto_cliente.unidade_localizacao_por_indice(1)

    login(page, dados_cliente)
    acessar_recebimento_transferencia_interna(page)
    consultar_transferencia(page, ug)

    if not selecionar_transferencia(page, ul):
        logger.warning("Pulando teste.")
        pytest.skip()

    efetuar_recebimento(page)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Recebimento de Transferência Interna Temporária.")
