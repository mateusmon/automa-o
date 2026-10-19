from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.solicitacao_materiais.finalizar_solicitacao_flow import (
    finalizar_solicitacao_materiais,
)
from flows.almoxarifado.movimentacao_interna.solicitacao_materiais.navegar_para_solicitacao_materiais_flow import (
    acessar_solicitacao_materiais,
)
from flows.almoxarifado.movimentacao_interna.solicitacao_materiais.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_solicitacao_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:

    logger.info("Iniciou teste de Solicitação de Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    ur = contexto_cliente.ur_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_solicitacao_materiais(page)
    preencher_dados_gerais(page, almoxarifado, ur, material)
    finalizar_solicitacao_materiais(page)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Solicitação de Materiais.")
