from loguru import logger
from playwright.sync_api import Page
from typing import Literal

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_resultado_consulta(page: Page, bem: dict[str, str]) -> Literal["entrada unica", "sem entradas", "entradas normais"]:
    """
    Verifica qual é o resultado da consulta.
    Pode ser:
    * sem entradas: Nenhuma entrada com esse número de material foi efetuada.
    * entrada unica: Apenas uma entrada com esse número de material foi efetuada, e consequentemente,
    a tela vai direto para essa entrada.
    * entradas normais: Há mais de uma entrada com esse número de material.
    """

    ctx = escopo(page)

    linha = ctx.locator("tbody tr")
    rows_count = linha.count()

    if ctx.get_by_role("heading", name="Dados do Bem").is_visible():
        return "entrada unica"
    elif not rows_count:
        logger.info(f"Não há entradas para o bem com nome {bem["nome"]} {bem["complemento"]}.")
        return "sem entradas"
    else:
        linha.first.locator('button[name^="submitPrint"]').click()
        aguardar_ajax_global(page)
        if ctx.locator("div[name='divErrorMsg']").is_visible():
            mensagem = ctx.locator("div[name='divErrorMsg']").text_content()
            logger.warning(mensagem)
            return "sem relatorios"
        return "entradas normais"
