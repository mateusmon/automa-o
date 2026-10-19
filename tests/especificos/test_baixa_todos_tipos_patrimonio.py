import pytest
from loguru import logger
from playwright.async_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.entrada_materiais.reportar_resultados_flow import (
    reportar_resultados,
)
from flows.patrimonio.movimentacao.baixa_bens.consulta_baixa_bens.consultar_baixa_bens_flow import (
    consultar_baixa_bens,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.navegar_para_baixa_bens_flow import (
    acessar_baixa_bens,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.preencher_itens_flow import (
    preencher_itens,
)
from flows.patrimonio.movimentacao.baixa_bens.listar_tipos_baixa_flow import (
    listar_tipos_baixa,
)
from flows.patrimonio.movimentacao.baixa_bens.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.shared.excluir_movimento_flow import (
    excluir_movimento,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from utils import trace


@pytest.mark.trace_por_combinacao
def test_baixa_todos_tipos(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou caso de teste de Baixa de Bens — todos os tipos disponíveis.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    fornecedor = contexto_cliente.fornecedor_padrao()
    bem = contexto_cliente.bem_padrao()

    with trace.trecho(page, "login e listagem de tipos"):
        login(page, dados_cliente)

        try:
            acessar_baixa_bens(page)
            tipos_baixa = listar_tipos_baixa(page)

            if not tipos_baixa:
                pytest.fail("Nenhum Tipo de Baixa disponível para execução.")

        except Exception as e:
            logger.error("Não foi possível listar os Tipos de Baixa: {}", e)
            _tentar_logout(page)
            pytest.fail(f"Não foi possível listar os Tipos de Baixa: {e}")

    logger.info("Tipos de Baixa encontrados ({}): {}", len(tipos_baixa), tipos_baixa)

    resultados = []

    for tipo_baixa in tipos_baixa:
        resultados.append(_executar_baixa(page, ug, fornecedor, bem, tipo_baixa))

    _tentar_logout(page)
    reportar_resultados("Baixa de Bens - todos os tipos", resultados)

    falhas = [resultado for resultado in resultados if resultado["status"] == "FALHA"]

    if falhas:
        pytest.fail(f"{len(falhas)} de {len(resultados)} tipos de baixa falharam.")


def _executar_baixa(
    page: Page, ug: dict, fornecedor: dict, bem: dict, tipo_baixa: str
) -> dict:
    rotulo = tipo_baixa
    etapa = "navegação"

    try:
        with trace.trecho(page, rotulo):
            acessar_baixa_bens(page)

            etapa = "dados gerais"
            preencher_dados_gerais(page, ug, tipo_baixa=tipo_baixa)

            etapa = "documentos"
            preencher_documentos(page, fornecedor)

            etapa = "seleção do bem"
            if not preencher_itens(page, ug, bem):
                raise RuntimeError("Não foi possível selecionar o bem para a baixa.")

            etapa = "impressão"
            imprimir_relatorio(page, timeout_geracao=250_000)

            etapa = "consulta da baixa"
            acessar_baixa_bens(page)

            if not consultar_baixa_bens(page, ug):
                raise RuntimeError("Baixa criada não foi encontrada para exclusão.")

            etapa = "exclusão"
            if not excluir_movimento(page):
                raise RuntimeError("Não foi possível excluir a baixa criada.")

        logger.success("[OK] {}\n", rotulo)

        return {"rotulo": rotulo, "status": "SUCESSO", "etapa": None, "erro": None}

    except Exception as e:
        return {
            "rotulo": rotulo,
            "status": "FALHA",
            "etapa": etapa,
            "erro": repr(e),
        }


def _tentar_logout(page: Page) -> None:
    try:
        logout(page)
    except Exception as e:
        logger.warning("Falha ao efetuar logout ao final do teste: {}", e)
