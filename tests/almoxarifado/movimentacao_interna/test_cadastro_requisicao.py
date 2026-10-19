from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.navegar_para_cadastro_requisicao_flow import (
    acessar_cadastro_requisicao,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.preencher_itens_flow import (
    preencher_itens,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_requisicao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Requisição.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur_padrao = contexto_cliente.ur_padrao()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_cadastro_requisicao(page)
    preencher_dados_gerais(page, ur_padrao, almoxarifado)
    preencher_itens(page, material)
    imprimir_relatorio(page, timeout_geracao= 250_000)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Requisição.")
