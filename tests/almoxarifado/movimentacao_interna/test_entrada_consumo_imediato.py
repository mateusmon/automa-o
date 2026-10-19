from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.entrada_materiais.acoes_escolher_endereco_flow import (
    acoes_escolher_endereco,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.entrada_consumo_imediato.acoes_escolher_ur_flow import (
    acoes_escolher_ur,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.escolher_finalidade_flow import (
    escolher_finalidade,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.finalizar_entrada_flow import (
    finalizar_entrada,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.navegar_para_entrada_materiais_flow import (
    acessar_entrada_materiais,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
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


def test_entrada_consumo_imediato(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Entrada Consumo Imediato.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    fornecedor = contexto_cliente.fornecedor_padrao()
    material = contexto_cliente.material_padrao()
    ur = contexto_cliente.ur_padrao()

    login(page, dados_cliente)
    acessar_entrada_materiais(page)
    escolher_finalidade(page, "CONSUMO IMEDIATO")
    preencher_dados_gerais(page, almoxarifado, fornecedor)
    preencher_documentos(page)
    preencher_materiais(page, material)
    acoes_escolher_endereco(page, material)
    acoes_escolher_ur(page, material, ur)
    finalizar_entrada(page)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Entrada Consumo Imediato.")
