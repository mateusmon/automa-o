"""Seleção de registros Genesis com identidade exata no grid de consulta."""

import re
import unicodedata

from loguru import logger
from playwright.sync_api import Frame, Page

from flows.corporativo.localidade.cadastro_cidade.consultar_cidade_flow import (
    consultar_cidade,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def normalizar_identificador(valor: str, ignorar_acentos: bool = False) -> str:
    """Normaliza espaços, caixa e, opcionalmente, acentuação de um identificador."""
    normalizado = " ".join(valor.split()).casefold()
    if ignorar_acentos:
        normalizado = "".join(
            caractere
            for caractere in unicodedata.normalize("NFD", normalizado)
            if unicodedata.category(caractere) != "Mn"
        )
    return normalizado


def decidir_linha_exata(
    linhas: list[list[str]], identificador: str, ignorar_acentos: bool = False
) -> int | None:
    """Retorna o índice da única linha com uma célula exatamente correspondente.

    Retorna ``None`` quando não há correspondência e falha em caso de duplicidade.
    """
    identificador_normalizado = normalizar_identificador(
        identificador, ignorar_acentos
    )
    indices = [
        indice
        for indice, celulas in enumerate(linhas)
        if any(
            normalizar_identificador(celula, ignorar_acentos)
            == identificador_normalizado
            for celula in celulas
        )
    ]

    if len(indices) > 1:
        raise RuntimeError(
            f"Identidade duplicada para '{identificador}': {len(indices)} linhas exatas."
        )
    return indices[0] if indices else None


def normalizar_nome_cidade(valor: str) -> str:
    """Normaliza o nome de Cidade, descartando somente o código de exibição."""
    sem_codigo = re.sub(r"^[A-Za-z]\d{1,2}\s+", "", valor.strip())
    return normalizar_identificador(sem_codigo, ignorar_acentos=True)


def verificar_cidade_existente(page: Page, nome: str) -> bool:
    """Confirma que a Cidade comum existe com ou sem acento, sem anexá-la.

    Cidade é pré-condição compartilhada e não é cadastrada pelos pilotos Genesis.
    O grid pode exibir um código técnico antes do nome; esse código não compõe a
    identidade da Cidade e é removido somente nesta verificação. Se a primeira
    busca não encontrar correspondência, repete a consulta sem os acentos.
    """
    logger.info("Iniciou verificação de Cidade '{}'.", nome)

    existe = _cidade_existe_no_resultado(page, nome)
    ctx = escopo(page)
    _cancelar_consulta(ctx, page)

    nome_sem_acento = "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", nome)
        if unicodedata.category(caractere) != "Mn"
    )
    if not existe and nome_sem_acento.casefold() != nome.casefold():
        logger.info(
            "Cidade '{}' não encontrada. Tentando nova consulta por '{}'.",
            nome,
            nome_sem_acento,
        )
        consultar_cidade(page, {"nome": nome_sem_acento})
        existe = _cidade_existe_no_resultado(page, nome)
        _cancelar_consulta(escopo(page), page)

    if existe:
        logger.info("Finalizou verificação de Cidade '{}'.", nome)
        return True

    logger.info("Finalizou verificação de Cidade '{}'.", nome)
    return False


def _cidade_existe_no_resultado(page: Page, nome: str) -> bool:
    """Procura a cidade no resultado da consulta atualmente aberto."""
    ctx = escopo(page)
    ctx.locator("span[name='searchResultSize']").wait_for(state="visible")
    linhas = ctx.locator("table[name='paginationTable'] tbody tr").all()
    cidade_normalizada = normalizar_nome_cidade(nome)
    return any(
        normalizar_nome_cidade(celula) == cidade_normalizada
        for linha in linhas
        for celula in linha.locator("td").all_inner_texts()
    )


def _cancelar_consulta(ctx: Page | Frame, page: Page) -> None:
    """Retorna da consulta sem alterar dados quando não há registro correspondente."""
    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)


def selecionar_registro_exato(
    page: Page,
    identificador: str,
    *,
    ignorar_acentos: bool = False,
    table_locator: str = "table[name='paginationTable'] tbody tr",
) -> bool:
    """Anexa a única linha cuja célula corresponde exatamente ao identificador.

    A comparação ignora caixa e espaços repetidos. A equivalência sem acento é
    opcional e restrita aos chamadores que a necessitam. Retorna ``False`` se não
    houver correspondência; em duplicidade, levanta ``RuntimeError`` antes de clicar.
    """
    logger.info("Iniciou seleção exata de '{}'.", identificador)

    ctx = escopo(page)
    resultado = ctx.locator("span[name='searchResultSize']")
    resultado.wait_for(state="visible")

    if resultado.inner_text().strip() == "0":
        logger.info("Nenhum resultado retornado para '{}'.", identificador)
        _cancelar_consulta(ctx, page)
        logger.info("Finalizou seleção exata de '{}'.", identificador)
        return False

    rows = ctx.locator(table_locator)
    linhas = [linha for linha in rows.all() if linha.is_visible()]
    if not linhas:
        raise RuntimeError(
            "A consulta retornou resultados, mas o grid não está disponível para "
            f"validar a identidade exata de '{identificador}'."
        )

    indice = decidir_linha_exata(
        [linha.locator("td").all_inner_texts() for linha in linhas],
        identificador,
        ignorar_acentos,
    )
    if indice is None:
        logger.info("Nenhuma identidade exata encontrada para '{}'.", identificador)
        _cancelar_consulta(ctx, page)
        logger.info("Finalizou seleção exata de '{}'.", identificador)
        return False

    clicar_com_ajax(ctx, linhas[indice].locator("button[name='submitUse']"))
    logger.info("Finalizou seleção exata de '{}'.", identificador)
    return True
