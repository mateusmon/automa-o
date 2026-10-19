import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.baixa.navegar_para_baixa_flow import (
    acessar_baixa,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_itens_flow import (
    preencher_itens,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_observacoes_flow import (
    preencher_observacoes,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_baixa_completa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Baixa Completa.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()
    destino = contexto_cliente.orgao_externo()

    login(page, dados_cliente)
    acessar_baixa(page)
    preencher_dados_gerais(page, almoxarifado, modalidade="DOAÇÃO", destino=destino, situacao="EM ANDAMENTO")
    preencher_documentos(page)
    preencher_observacoes(page, finalidade="NOTA TÉCNICA")

    if not preencher_itens(page, material, quantidade="1", teste_linha=True):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Baixa Completa.")
