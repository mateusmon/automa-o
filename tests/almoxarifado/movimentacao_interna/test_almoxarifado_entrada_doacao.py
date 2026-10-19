from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.entrada_materiais.acoes_escolher_endereco_flow import (
    acoes_escolher_endereco,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.entrada_doacao.escolher_fornecedor_manualmente_flow import (
    escolher_fornecedor_manualmente,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.entrada_doacao.preencher_datas_dados_gerais_flow import (
    preencher_datas_dados_gerais,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.entrada_doacao.preencher_somente_almoxarifado_flow import (
    preencher_somente_almoxarifado,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.escolher_tipo_entrada_flow import (
    escolher_tipo_entrada,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.finalizar_entrada_flow import (
    finalizar_entrada,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.navegar_para_entrada_materiais_flow import (
    acessar_entrada_materiais,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_almoxarifado_entrada_doacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Entrada de Doação.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_entrada_materiais(page)
    escolher_tipo_entrada(page, "DOAÇÃO")
    preencher_somente_almoxarifado(page, almoxarifado)
    escolher_fornecedor_manualmente(page)
    preencher_datas_dados_gerais(page)
    preencher_documentos(page)
    preencher_materiais(page, material)
    acoes_escolher_endereco(page, material)
    finalizar_entrada(page)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Entrada de Doação.")
