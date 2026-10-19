"""
Teste ESPECIAL de Entrada Completa.

Diferente dos demais testes de entrada, este exercita TODAS as combinações de
Tipo de Entrada x Finalidade disponíveis no formulário, criando uma entrada
(com observação) para cada combinação. São dois laços aninhados: para cada tipo
de entrada, percorre todas as finalidades válidas daquele tipo. Tipos e
finalidades já chegam como lista completa antes da varredura começar
(`listar_tipos_entrada`/`listar_finalidades` leem o <select> de uma vez) —
por isso a iteração é um `for` direto, sem recursão nem `while`: não há
descoberta item-a-item por índice que justifique isso.

Nenhuma combinação individual interrompe a varredura — cada uma roda isolada
dentro de `_executar_entrada`, que nunca propaga exceção. O teste como um
todo, porém, NÃO é "sempre verde": depois que todas as combinações rodaram,
o relatório foi logado e o logout foi feito, se sobrou alguma falha
classificada como inesperada (`"FALHA"`, diferente de `"FALHA_ESPERADA"`),
o teste falha de verdade via `pytest.fail()` — para que CI/Sentinela
enxerguem que algo quebrou.

Premissas importantes:
- Os tipos de entrada e as finalidades são descobertos DINAMICAMENTE a partir dos
  <select> da página (não há lista fixa), pois variam por cliente/versão.
- Sabe-se que a entrada do tipo "Compra" (orçamentária) NÃO conclui com os dados
  genéricos deste teste — sua falha é ESPERADA (ver `_falha_esperada`).
"""

import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.evento.navegar_para_evento_flow import (
    acessar_evento,
)
from flows.almoxarifado.gestao_de_compras.evento.preencher_dados_gerais_flow import (
    preencher_dados_gerais as preencher_dados_gerais_evento,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.acoes_escolher_endereco_flow import (
    acoes_escolher_endereco,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.acoes_escolher_evento_flow import (
    acoes_escolher_evento,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.consultar_evento_flow import (
    consultar_evento,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.entrada_consumo_imediato.acoes_escolher_ur_flow import (
    acoes_escolher_ur,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.entrada_observacao.preencher_observacoes_flow import (
    preencher_observacoes,
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
from flows.almoxarifado.movimentacao_interna.entrada_materiais.listar_finalidades_flow import (
    listar_finalidades,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.listar_tipos_entrada_flow import (
    listar_tipos_entrada,
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
from flows.almoxarifado.movimentacao_interna.entrada_materiais.reportar_resultados_flow import (
    reportar_resultados,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from utils import trace

NOME_EVENTO = "EVENTO AUTOMATIZADO PARA ENTRADA"


@pytest.mark.trace_por_combinacao
def test_entrada_completa(page: Page, contexto_cliente: ContextoCliente) -> None:
    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    fornecedor = contexto_cliente.fornecedor_padrao()
    material = contexto_cliente.material_padrao()
    orgao_externo = contexto_cliente.orgao_externo()
    ur = contexto_cliente.ur_padrao()

    logger.info("Iniciou teste de Entrada Completa (todos os tipos x finalidades).")

    with trace.trecho(page, "login, evento e listagem de tipos"):
        login(page, dados_cliente)
        _garantir_evento(page)

        # Descobre dinamicamente todos os tipos de entrada disponíveis.
        try:
            acessar_entrada_materiais(page)
            tipos = listar_tipos_entrada(page)
        except Exception as e:
            logger.error(
                "Não foi possível listar os tipos de entrada — abortando sem falhar: {}",
                e,
            )
            _tentar_logout(page)
            pytest.fail(f"Não foi possível listar os tipos de entrada: {e}")

    logger.info("Tipos de entrada encontrados ({}): {}", len(tipos), tipos)

    resultados: list[dict] = []

    for tipo in tipos:
        # As finalidades dependem do tipo selecionado — descobre a cada tipo.
        finalidades = _descobrir_finalidades(page, tipo)

        logger.info("Tipo '{}' -> finalidades: {}", tipo, finalidades or ["(padrão)"])

        for finalidade in finalidades:
            resultados.append(
                _executar_entrada(
                    page,
                    tipo,
                    finalidade,
                    almoxarifado,
                    fornecedor,
                    material,
                    orgao_externo,
                    ur,
                )
            )

    _tentar_logout(page)
    reportar_resultados(
        "Entrada de Materiais — Almoxarifado (todos os tipos x finalidades)", resultados
    )

    logger.success("Finalizou teste de Entrada Completa.")

    falhas_inesperadas = [r for r in resultados if r["status"] == "FALHA"]
    if falhas_inesperadas:
        pytest.fail(
            f"{len(falhas_inesperadas)} de {len(resultados)} combinação(ões) falharam de forma "
            "inesperada. Veja o RESUMO logado acima para o detalhe de cada uma (rótulo, etapa e erro)."
        )


def _garantir_evento(page: Page) -> None:
    """
    Garantir que evento já exista no sistema.
    """
    ha_caminho = acessar_evento(page)
    if not ha_caminho:
        logger.warning("Pulando teste.")
        pytest.skip()
    existe_evento = consultar_evento(page, NOME_EVENTO)
    if not existe_evento:
        ha_caminho = acessar_evento(page)
        if not ha_caminho:
            logger.warning("Pulando teste.")
            pytest.skip()
        preencher_dados_gerais_evento(page, NOME_EVENTO)


def _descobrir_finalidades(page: Page, tipo: str) -> list[str | None]:
    """
    Abre um formulário novo, seleciona o tipo e lê as finalidades disponíveis.
    Retorna `[None]` quando não há finalidades (roda uma vez com o padrão).
    """
    try:
        with trace.trecho(page, f"descobrir finalidades - {tipo}"):
            acessar_entrada_materiais(page)
            escolher_tipo_entrada(page, tipo)
            finalidades: list[str | None] = [f for f in listar_finalidades(page)]
        return finalidades if finalidades else [None]
    except Exception as e:
        logger.warning("Não foi possível listar finalidades do tipo '{}': {}", tipo, e)
        return [None]


def _executar_entrada(
    page: Page,
    tipo: str,
    finalidade: str | None,
    almoxarifado: dict,
    fornecedor: dict,
    material: dict,
    orgao_externo: dict,
    ur: dict,
) -> dict:
    """
    Executa uma entrada completa (com observação e impressão) para uma
    combinação tipo x finalidade. Nunca propaga exceção: em caso de erro,
    registra a etapa que falhou e devolve o resultado classificado.
    """
    rotulo = f"{tipo} | {finalidade or '(finalidade padrão)'}"
    etapa = "navegação"
    tipo_nao_utilizado = False

    try:
        with trace.trecho(
            page,
            rotulo,
            salvar_se=lambda e: not (_falha_esperada(tipo) or tipo_nao_utilizado),
        ):
            acessar_entrada_materiais(page)

            etapa = "escolher tipo"
            escolher_tipo_entrada(page, tipo)

            etapa = "escolher finalidade"
            escolher_finalidade(page, finalidade)

            etapa = "dados gerais"
            preencher_dados_gerais(page, almoxarifado, fornecedor, orgao_externo)

            etapa = "documentos"
            preencher_documentos(page)

            etapa = "materiais"
            tipo_nao_utilizado = preencher_materiais(page, material)

            etapa = "escolher UR (se aplicável)"
            acoes_escolher_ur(page, material, ur)

            etapa = "escolher Evento (se aplicável)"
            acoes_escolher_evento(page, material)

            etapa = "observações"
            preencher_observacoes(page, material)

            etapa = "endereço"
            acoes_escolher_endereco(page, material)

            etapa = "finalizar"
            finalizar_entrada(page)

            etapa = "impressão"
            imprimir_relatorio(
                page, relatorio_preferido="AX0052", timeout_visualizacao=5_000
            )

        logger.success("[OK] {}\n", rotulo)
        return {"rotulo": rotulo, "status": "SUCESSO", "etapa": None, "erro": None}

    except Exception as e:
        esperada = _falha_esperada(tipo) or tipo_nao_utilizado
        status = "FALHA_ESPERADA" if esperada else "FALHA"
        log = logger.warning if esperada else logger.error
        log("[{}] {} — falhou em '{}': {}", status, rotulo, etapa, e)
        return {"rotulo": rotulo, "status": status, "etapa": etapa, "erro": repr(e)}


def _tentar_logout(page: Page) -> None:
    """Efetua logout sem propagar exceção (evita disparar o popup de falha)."""
    try:
        logout(page)
    except Exception as e:
        logger.warning("Falha ao efetuar logout ao final do teste: {}", e)


def _falha_esperada(tipo: str) -> bool:
    """
    Indica se a falha de um tipo de entrada é conhecida/esperada.

    A entrada do tipo "Compra" (orçamentária) não conclui com os dados
    genéricos deste teste (exige empenho/orçamento não preenchido aqui). As
    variantes "Compra extra-orçamentária" e "Compra por importação" NÃO
    entram nessa exceção.
    """
    t = tipo.upper()
    return "COMPRA" in t and "EXTRA" not in t and "IMPORT" not in t
