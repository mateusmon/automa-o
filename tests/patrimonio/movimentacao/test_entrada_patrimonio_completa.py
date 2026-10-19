from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.entrada_bens.editar_primeiro_documento_com_anexo_flow import (
    editar_primeiro_documento_com_anexo,
)
from flows.patrimonio.movimentacao.entrada_bens.escolher_tipo_aquisição_flow import (
    escolher_tipo_aquisição,
)
from flows.patrimonio.movimentacao.entrada_bens.escolher_tipo_bem_flow import (
    escolher_tipo_bem,
)
from flows.patrimonio.movimentacao.entrada_bens.navegar_para_entrada_bens_flow import (
    acessar_entrada_bens,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_dados_gerais_sem_autocomplete_flow import (
    preencher_dados_gerais_sem_autocomplete,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_todos_documentos_flow import (
    preencher_todos_documentos,
)
from flows.patrimonio.movimentacao.entrada_bens.realizar_acoes_completo_flow import (
    realizar_acoes_completo,
)
from flows.patrimonio.movimentacao.entrada_bens.verificar_existencia_siaf_flow import (
    verificar_existencia_siaf,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_entrada_bens_completa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Entrada Completa de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    fornecedor = contexto_cliente.fornecedor_padrao()
    bem = contexto_cliente.bem_por_indice(18)
    
    login(page, dados_cliente)
    acessar_entrada_bens(page)
    escolher_tipo_bem(page, "DE TERCEIROS")
    escolher_tipo_bem(page, "CONTABILIZADO")

    # Essa verificação foi criada só para lidar com SEADPB e SEADPB ADAPT
    if verificar_existencia_siaf(page):
        escolher_tipo_aquisição(page, "IMPORTAÇÃO (N/ORÇ)")
    else:
        escolher_tipo_aquisição(page, "DOAÇÂO")
        escolher_tipo_aquisição(page, "COMPRA")
    
    preencher_dados_gerais_sem_autocomplete(page, ug, fornecedor)
    preencher_todos_documentos(page, fornecedor)
    editar_primeiro_documento_com_anexo(page)
    preencher_materiais(page, bem)
    realizar_acoes_completo(page)
    imprimir_relatorio(page, timeout_geracao=350_000)
    logout(page)

    logger.success("Finalizou teste de Entrada Completa de Bens.")
