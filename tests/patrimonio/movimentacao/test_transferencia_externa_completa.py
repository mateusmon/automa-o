import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.transferencia_externa.navegar_para_transferencia_externa import (
    acessar_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.restaurar_transferencia_externa_flow import (
    restaurar_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.nova_transferencia_externa_flow import (
    nova_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.preencher_dados_gerais_completo_flow import (
    preencher_dados_gerais_completo,
)
from flows.patrimonio.movimentacao.transferencia_externa.selecionar_objetivo_flow import (
    selecionar_objetivo,
)
from flows.patrimonio.movimentacao.transferencia_externa.preencher_documentos_associados_flow import (
    preencher_documentos_associados,
)
from flows.patrimonio.movimentacao.transferencia_externa.editar_documentos_associados_flow import (
    editar_documentos_associados,
)
from flows.patrimonio.movimentacao.transferencia_externa.preencher_itens_transferencia_externa_flow import (
    preencher_itens_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.preencher_observacoes_flow import (
    preencher_observacoes,
)
from flows.patrimonio.movimentacao.transferencia_externa.visualizar_transferencia_externa_flow import (
    visualizar_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.confirmar_transferencia_externa_flow import (
    confirmar_transferencia_externa,
)
from flows.patrimonio.movimentacao.transferencia_externa.imprimir_relatorios_transferencia_externa_flow import (
    imprimir_relatorios_transferencia_externa,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_transferencia_externa_completa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Transferência Externa Completa.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()
    fornecedor = contexto_cliente.fornecedor_padrao()
    funcionario = contexto_cliente.funcionario_padrao()
    
    login(page, dados_cliente)
    acessar_transferencia_externa(page)
    restaurar_transferencia_externa(page)
    nova_transferencia_externa(page)
    preencher_dados_gerais_completo(page, ug, funcionario, fornecedor)
    selecionar_objetivo(page, "EVENTO")
    selecionar_objetivo(page, "MANUTENÇÃO")

    if preencher_documentos_associados(page, fornecedor):
        editar_documentos_associados(page)
    else:
        logger.info("Cliente não possui documentos associados.")

    if not preencher_itens_transferencia_externa(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    preencher_observacoes(page)
    visualizar_transferencia_externa(page)
    confirmar_transferencia_externa(page)
    imprimir_relatorios_transferencia_externa(page)
    logout(page)
    
    logger.success("Finalizou teste de Transferência Externa Completa.")
    