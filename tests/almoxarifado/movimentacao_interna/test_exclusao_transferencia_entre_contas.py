import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.consulta_trasferencia_entre_contas.consultar_transferencia_entre_contas_flow import (
    consultar_transferencia_entre_contas,
)
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.navegar_para_transferencia_entre_contas_flow import (
    acessar_transferencia_entre_contas,
)
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.selecionar_transferencia_flow import (
    selecionar_transferencia,
)
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.verificar_aviso_ugs_abertas_flow import (
    verificar_aviso_ugs_abertas,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_transferencia_entre_contas(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Transferência entre Contas.")

    dados_cliente = contexto_cliente.dados_cliente()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_transferencia_entre_contas(page)

    if not verificar_aviso_ugs_abertas(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    consultar_transferencia_entre_contas(page, material)

    if not selecionar_transferencia(page, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Transferência entre Contas.")
