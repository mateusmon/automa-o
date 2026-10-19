from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.entrada_bens.escolher_tipo_aquisição_flow import (
    escolher_tipo_aquisição,
)
from flows.patrimonio.movimentacao.entrada_bens.escolher_tipo_bem_flow import (
    escolher_tipo_bem,
)
from flows.patrimonio.movimentacao.entrada_bens.navegar_para_entrada_bens_flow import (
    acessar_entrada_bens,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_detalhamento_flow import (
    preencher_detalhamento,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_multiplos_materiais_flow import (
    preencher_multiplos_materiais,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_todos_documentos_flow import (
    preencher_todos_documentos,
)
from flows.patrimonio.movimentacao.entrada_bens.realizar_acoes_multiplos_bens_flow import (
    realizar_acoes_multiplos_bens,
)
from flows.patrimonio.movimentacao.entrada_bens.verificar_existencia_siaf_flow import (
    verificar_existencia_siaf,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_entrada_20_materiais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Entrada de Bens com 20 Materiais.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    fornecedor = contexto_cliente.fornecedor_padrao()
    bens_20 = contexto_cliente.bens_por_quantidade()

    login(page, dados_cliente)
    acessar_entrada_bens(page)
    escolher_tipo_bem(page, "DE TERCEIROS")
    escolher_tipo_bem(page, "CONTABILIZADO")
    preencher_dados_gerais(page, ug)

    if verificar_existencia_siaf(page):
        preencher_detalhamento(page, fornecedor, tipo="IMPORTAÇÃO (N/ORÇ)")
    else:
        escolher_tipo_aquisição(page, "DOAÇÂO")
        preencher_detalhamento(page, fornecedor, tipo="COMPRA")

    preencher_todos_documentos(page, fornecedor)
    preencher_multiplos_materiais(page, bens_20)
    realizar_acoes_multiplos_bens(page, len(bens_20))
    imprimir_relatorio(page, timeout_geracao=350_000)
    logout(page)

    logger.success("Finalizou teste de Entrada de Bens com 20 Materiais.")
