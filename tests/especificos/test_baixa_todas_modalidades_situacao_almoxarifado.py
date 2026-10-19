import pytest
from loguru import logger
from playwright.async_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.baixa.consulta_baixa_material.consultar_baixa_material_flow import (
    consultar_baixa_material,
)
from flows.almoxarifado.movimentacao_interna.baixa.escolher_modalidade_flow import (
    escolher_modalidade,
)
from flows.almoxarifado.movimentacao_interna.baixa.exclusao_baixa_material.excluir_baixa_material_flow import (
    excluir_baixa_material,
)
from flows.almoxarifado.movimentacao_interna.baixa.listar_modalidades_baixa_flow import (
    listar_modalidades_baixa,
)
from flows.almoxarifado.movimentacao_interna.baixa.listar_situacoes_baixa_flow import (
    listar_situacoes_baixa,
)
from flows.almoxarifado.movimentacao_interna.baixa.navegar_para_baixa_flow import (
    acessar_baixa,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_itens_flow import (
    preencher_itens,
)
from flows.almoxarifado.movimentacao_interna.baixa.preencher_observacoes_flow import (
    preencher_observacoes,
)
from flows.almoxarifado.movimentacao_interna.baixa.selecionar_baixa_flow import (
    selecionar_baixa,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.reportar_resultados_flow import (
    reportar_resultados,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from utils import trace


@pytest.mark.trace_por_combinacao
def test_baixa_todas_modalidades_situacao_almoxarifado(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    logger.info("Iniciou teste Baixa Todos os Tipos Almoxarifado.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    destino = contexto_cliente.orgao_externo()
    material = contexto_cliente.material_padrao()

    with trace.trecho(page, "login e listagem de modalidades"):
        login(page, dados_cliente)

        try:
            acessar_baixa(page)
            modalidades = listar_modalidades_baixa(page)
        except Exception as e:
            logger.error("Não foi possível listar as modalidades da baixa: {}", e)
            _tentar_logout(page)
            pytest.fail(f"Não foi possível listar as modalidades da baixa: {e}")

    logger.info(
        "Modalidades da baixa encontradas ({}): {}", len(modalidades), modalidades
    )

    resultados: list[dict] = []

    for modalidade in modalidades:
        with trace.trecho(page, f"descobrir situações - {modalidade}"):
            situacoes = listar_situacoes_baixa(page)

        logger.info("Modalidade '{}' -> situação '{}'", modalidade, situacoes)

        for situacao in situacoes:
            resultados.append(
                _executar_baixa(
                    page, modalidade, situacao, almoxarifado, destino, material
                )
            )

    _tentar_logout(page)
    reportar_resultados(
        "Baixa de Materiais - Almoxarifado (todos as modalidades x situações)",
        resultados,
    )

    logger.success("Finalizou teste Baixa Todos os Tipos Almoxarifado.")

    falhas = [resultado for resultado in resultados if resultado["status"] == "FALHA"]
    if falhas:
        pytest.fail(f"{len(falhas)} de {len(resultados)} combinações de baixa falharam.")


def _executar_baixa(
    page: Page,
    modalidade: str,
    situacao: str,
    almoxarifado: dict[str, str],
    destino: dict[str, str],
    material,
) -> dict:
    rotulo = f"{modalidade} | {situacao}"
    etapa = "navegação"

    try:
        with trace.trecho(page, rotulo):
            acessar_baixa(page)

            etapa = "escolher modalidade"
            escolher_modalidade(page, modalidade)

            etapa = "dados gerais"
            preencher_dados_gerais(
                page, almoxarifado, modalidade=None, destino=destino, situacao=situacao
            )

            etapa = "documentos"
            preencher_documentos(page)

            etapa = "observação"
            preencher_observacoes(page)

            etapa = "itens"
            preencher_itens(page, material, "1")

            etapa = "impressão"
            imprimir_relatorio(page)

            etapa = "navegação"
            acessar_baixa(page)

            etapa = "consulta"
            consultar_baixa_material(page, almoxarifado, material)

            etapa = "selecionar baixa"
            selecionar_baixa(page, material)

            etapa = "exclusão"
            excluir_baixa_material(page)

        logger.success("[OK] {} \n", rotulo)
        return {"rotulo": rotulo, "status": "SUCESSO", "etapa": None, "erro": None}

    except Exception as e:
        status = "FALHA"
        log = logger.error
        log("[{}] {} - falhou em '{}': '{}'", status, rotulo, etapa, e)
        return {"rotulo": rotulo, "status": status, "etapa": etapa, "erro": repr(e)}


def _tentar_logout(page: Page) -> None:
    try:
        logout(page)
    except Exception as e:
        logger.warning("Falha ao efeturar logout ao final do teste: {}", e)
