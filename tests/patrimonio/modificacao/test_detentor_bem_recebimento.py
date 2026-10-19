import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.detentor_bem_recebimento.consultar_transferencia_flow import (
    consultar_transferencia,
)
from flows.patrimonio.modificacao.detentor_bem_recebimento.navegar_para_detentor_bem_recebimento_flow import (
    acessar_detentor_bem_recebimento,
)
from flows.patrimonio.modificacao.detentor_bem_recebimento.selecionar_transferencia_flow import (
    selecionar_transferencia,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_detentor_bem_recebimento(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Detentor do Bem - Recebimento.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    funcionario = contexto_cliente.funcionario_padrao()

    login(page, dados_cliente)
    acessar_detentor_bem_recebimento(page)
    consultar_transferencia(page, ug)

    if not selecionar_transferencia(page, funcionario):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Detentor do Bem - Recebimento.")
