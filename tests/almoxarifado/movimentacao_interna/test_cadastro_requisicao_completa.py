from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.navegar_para_cadastro_requisicao_flow import (
    acessar_cadastro_requisicao,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.preencher_dados_gerais_completo_flow import (
    preencher_dados_gerais_completo,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.preencher_itens_completo_flow import (
    preencher_itens_completo,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.preencher_observacao_flow import (
    preencher_observacao,
)
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.preencher_patrimonio_flow import (
    preencher_patrimonio,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_requisicao_completa(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    logger.info("Iniciou teste de Cadastro de Requisição Completa.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ur = contexto_cliente.ur_padrao()
    material1 = contexto_cliente.material_padrao()
    material2 = contexto_cliente.material_por_indice(1)

    login(page, dados_cliente)
    acessar_cadastro_requisicao(page)
    preencher_dados_gerais_completo(page, almoxarifado, ur)
    preencher_itens_completo(page, material1, "2401")
    preencher_itens_completo(page, material2, "2401")
    preencher_patrimonio(page)
    preencher_observacao(page)
    imprimir_relatorio(page, timeout_geracao=250_000)
    logout(page)

    logger.success("Finalizou teste de Cadastro de Requisição Completa.")
