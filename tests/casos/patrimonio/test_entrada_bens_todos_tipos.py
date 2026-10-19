"""
Caso de teste especial: varre TODAS as combinações de Tipo de
Bem x Forma de Operação disponíveis na Entrada de Bens, com observação.

A quantidade de Tipos de Bem e de Formas de Operação varia por cliente, então
a varredura não tem um número fixo de repetições. Como a arquitetura do
projeto não permite `for`/`while` em arquivos de teste nem um flow chamando
outro flow, a repetição é implementada por recursão em funções auxiliares
deste próprio arquivo — mesmo padrão de orquestração local de
tests/casos/almoxarifado/test_ciclo_requisicao.py — que chamam os flows
diretamente em sequência, um por combinação.

A SEADPB não permite entradas do tipo de Forma de Operação "COMPRA" (ver
GUIA_TESTES.md, seção "Entrada de Materiais — SEADPB") — essa falha é
esperada e é destacada separadamente no relatório final.
"""

import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_interna.entrada_materiais.reportar_resultados_flow import (
    reportar_resultados,
)
from flows.patrimonio.movimentacao.entrada_bens.escolher_forma_operacao_flow import (
    escolher_forma_operacao,
)
from flows.patrimonio.movimentacao.entrada_bens.escolher_tipo_bem_flow import (
    escolher_tipo_bem,
)
from flows.patrimonio.movimentacao.entrada_bens.listar_formas_operacao_flow import (
    listar_formas_operacao,
)
from flows.patrimonio.movimentacao.entrada_bens.listar_tipos_bem_flow import (
    listar_tipos_bem,
)
from flows.patrimonio.movimentacao.entrada_bens.navegar_para_entrada_bens_flow import (
    acessar_entrada_bens,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_observacoes_flow import (
    preencher_observacoes,
)
from flows.patrimonio.movimentacao.entrada_bens.preencher_ug_flow import preencher_ug
from flows.patrimonio.movimentacao.entrada_bens.realizar_acoes_flow import (
    realizar_acoes,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from utils import trace

# Tipos de Entrada com falha esperada (SEADPB)
TIPOS_FALHA_ESPERADA = ("COMPRA",)


@pytest.mark.trace_por_combinacao
def test_entrada_bens_todos_tipos(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    logger.info(
        "Iniciou caso de teste de Entrada de Bens — todos os tipos e finalidades disponíveis."
    )

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    fornecedor = contexto_cliente.fornecedor_padrao()
    bem = contexto_cliente.bem_padrao()

    with trace.trecho(page, "login e listagem de tipos"):
        login(page, dados_cliente)

        try:
            acessar_entrada_bens(page)
            preencher_ug(page, ug)
            tipos_bem = listar_tipos_bem(page)

            if not tipos_bem:
                pytest.fail("Nenhum Tipo de Bem disponível para execução.")

        except Exception as e:
            logger.error("Não foi possível listar os Tipos de Bem: {}", e)
            _tentar_logout(page)
            pytest.fail(f"Não foi possível listar os Tipos de Bem: {e}")

    logger.info("Tipos de Bem encontrados ({}): {}", len(tipos_bem), tipos_bem)

    resultados: list[dict] = []

    for tipo_bem in tipos_bem:
        # As formas de operação dependem do tipo de bem selecionado — descobre a cada tipo.
        formas = _descobrir_formas_operacao(page, ug, tipo_bem, resultados)

        logger.info(
            "Tipo de Bem '{}' -> Formas de Operação: {}",
            tipo_bem,
            formas or ["(nenhuma — falha na descoberta)"],
        )

        for forma in formas:
            resultados.append(
                _executar_entrada(page, ug, fornecedor, bem, tipo_bem, forma)
            )

    _tentar_logout(page)
    reportar_resultados(
        "Entrada de Bens — Patrimônio (todos os tipos x formas de operação)", resultados
    )

    logger.success(
        "Finalizou caso de teste de Entrada de Bens — todos os tipos e formas de operação disponíveis."
    )

    falhas_inesperadas = [r for r in resultados if r["status"] == "FALHA"]
    if falhas_inesperadas:
        pytest.fail(
            f"{len(falhas_inesperadas)} de {len(resultados)} combinação(ões) falharam de forma "
            "inesperada. Veja o RESUMO logado acima para o detalhe de cada uma (rótulo, etapa e erro)."
        )


def _descobrir_formas_operacao(
    page: Page, ug: dict, tipo_bem: str, resultados: list[dict]
) -> list[str | None]:
    """
    Abre um formulário novo, seleciona a UG e o Tipo de Bem, e lê as Formas
    de Operação disponíveis.

    Retorna `[None]` quando a listagem terminou normalmente e não encontrou
    nenhuma opção, roda uma vez com a forma padrão da
    interface. Se a descoberta falhar por erro técnico (navegação, timeout,
    elemento não encontrado etc.), NÃO retorna `[None]` — isso esconderia a
    falha como se fosse simples ausência de opções. Em vez disso, registra
    um resultado com status "FALHA" em `resultados` e devolve lista vazia,
    para que o `for forma in formas:` do chamador não execute nenhuma
    combinação e a falha apareça no relatório final e no `pytest.fail()`.
    """
    try:
        with trace.trecho(page, f"descobrir formas - {tipo_bem}"):
            acessar_entrada_bens(page)
            preencher_ug(page, ug)
            escolher_tipo_bem(page, tipo_bem)
            formas = listar_formas_operacao(page)
        return formas if formas else [None]
    except Exception as e:
        logger.error(
            "Falha ao descobrir Formas de Operação do Tipo de Bem '{}': {}", tipo_bem, e
        )
        resultados.append(
            {
                "rotulo": f"{tipo_bem} | (descoberta de Formas de Operação)",
                "status": "FALHA",
                "etapa": "descobrir Formas de Operação",
                "erro": repr(e),
            }
        )
        return []


def _executar_entrada(
    page: Page,
    ug: dict,
    fornecedor: dict,
    bem: dict,
    tipo_bem: str,
    forma: str | None,
) -> dict:
    """
    Executa uma entrada completa (com observação e impressão) para uma
    combinação Tipo de Bem x Forma de Operação. Nunca propaga exceção: em
    caso de erro, registra a etapa que falhou e devolve o resultado
    classificado.
    """
    rotulo = f"{tipo_bem} | {forma or '(forma padrão)'}"
    etapa = "navegação"

    try:
        with trace.trecho(page, rotulo, salvar_se=lambda e: not _falha_esperada(forma)):
            acessar_entrada_bens(page)

            etapa = "preencher UG"
            preencher_ug(page, ug)

            etapa = "escolher Tipo de Bem"
            escolher_tipo_bem(page, tipo_bem)

            etapa = "escolher Forma de Operação"
            escolher_forma_operacao(page, forma, fornecedor)

            etapa = "documentos"
            preencher_documentos(page)

            etapa = "observações"
            preencher_observacoes(page)

            etapa = "materiais"
            preencher_materiais(page, bem)

            etapa = "ações finais"
            realizar_acoes(page)

            etapa = "impressão"
            imprimir_relatorio(page, pular_teste=False)

        logger.success("[OK] {}\n", rotulo)
        return {"rotulo": rotulo, "status": "SUCESSO", "etapa": None, "erro": None}

    except Exception as e:
        esperada = _falha_esperada(forma)
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


def _falha_esperada(forma: str | None) -> bool:
    """
    Indica se a falha de uma Forma de Operação é conhecida/esperada.
    """
    return forma is not None and forma.strip().upper() in TIPOS_FALHA_ESPERADA
