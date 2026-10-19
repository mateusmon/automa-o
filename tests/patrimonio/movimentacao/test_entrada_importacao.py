import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.entrada_bens.navegar_para_entrada_bens_flow import (
    acessar_entrada_bens,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_detalhamento_flow import (
    preencher_detalhamento,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.patrimonio.movimentacao.entrada_bens.realizar_acoes_flow import (
    realizar_acoes,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout

# Aqui você pode colocar a quantidade de itens que você quer que
# o teste adicione, a posição representa qual local no ordem.yaml
# está a chamada do teste que deve ter essa quantidade
_QUANTIDADES_POR_POSICAO = {
    1: "1",
    2: "10",
    3: "4",
}


def test_entrada_importacao(
    page: Page, contexto_cliente: ContextoCliente, posicao_ordem: int
) -> None:
    logger.info("Iniciou teste de Entrada de Bem tipo Importação (N/ORÇ).")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    fornecedor = contexto_cliente.fornecedor_padrao()
    bem = contexto_cliente.bem_padrao()
    quantidade = "1"

    login(page, dados_cliente)
    acessar_entrada_bens(page)
    preencher_dados_gerais(page, ug)

    if not preencher_detalhamento(page, fornecedor, "IMPORTAÇÃO (N/ORÇ)"):
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_documentos(page)
    preencher_materiais(page, bem, quantidade)
    realizar_acoes(page)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Entrada de Bem tipo Importação (N/ORÇ).")
