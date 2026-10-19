from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.entrada_materiais.acoes_escolher_endereco_flow import (
    acoes_escolher_endereco,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.editar_primeiro_documento_com_anexo_flow import (
    editar_primeiro_documento_com_anexo,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.escolher_finalidade_flow import (
    escolher_finalidade,
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
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_dados_gerais_sem_autocomplete_flow import (
    preencher_dados_gerais_sem_autocomplete,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_todos_documentos_flow import (
    preencher_todos_documentos,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.selecionar_ur_material_flow import (
    selecionar_ur_material,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.verificar_existencia_siaf_flow import (
    verificar_existencia_siaf,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_entrada_completa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Entrada Completa.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    fornecedor = contexto_cliente.fornecedor_padrao()
    material1 = contexto_cliente.material_padrao()
    material2 = contexto_cliente.material_por_indice(1)

    login(page, dados_cliente)
    acessar_entrada_materiais(page)
    escolher_tipo_entrada(page, "EXTRA")
    ha_siaf = verificar_existencia_siaf(page)
    if ha_siaf:
        escolher_tipo_entrada(page, "IMPORTAÇÃO (N/ORÇ)")
    else:
        escolher_tipo_entrada(page, "COMPRA")
        escolher_finalidade(page, "ESTOQUE")
    preencher_dados_gerais_sem_autocomplete(page, almoxarifado, fornecedor)
    preencher_todos_documentos(page)
    editar_primeiro_documento_com_anexo(page)
    preencher_materiais(page, material1, "2401")
    selecionar_ur_material(page)
    acoes_escolher_endereco(page, material1)
    preencher_materiais(page, material2, "2401")
    selecionar_ur_material(page)
    acoes_escolher_endereco(page, material2)
    finalizar_entrada(page)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Entrada Completa.")
