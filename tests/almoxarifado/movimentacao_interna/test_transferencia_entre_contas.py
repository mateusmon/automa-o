import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.navegar_para_transferencia_entre_contas_flow import (
    acessar_transferencia_entre_contas,
)
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.preencher_observacao_flow import (
    preencher_observacao,
)
from flows.almoxarifado.movimentacao_interna.transferencia_entre_contas.verificar_aviso_ugs_abertas_flow import (
    verificar_aviso_ugs_abertas,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_transferencia_entre_contas(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Transferência entre Contas.")

    dados_cliente = contexto_cliente.dados_cliente()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_transferencia_entre_contas(page)

    if not verificar_aviso_ugs_abertas(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_dados_gerais(page, material)
    preencher_observacao(page, material)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Transferência entre Contas.")
