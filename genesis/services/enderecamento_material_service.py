import re

from loguru import logger
from playwright.sync_api import Page, expect

from navigation.navegar_para_enderecamento import acessar_enderecamento
from utils.espera import (
    aguardar_ajax_global,
    preencher_campo,
)
from utils.versao_gen import escopo, get_versao


def enderecamento_existe(page: Page, almoxarifado: str, material: str, endereco: dict) -> bool:
    """
    Returns True if enderecamento exists.
    """

    # Navigation
    if not acessar_enderecamento(page):
        logger.warning("Menu 'Endereçamento de Material' não disponível para este cliente. Ignorando verificação de endereçamento.")
        return False

    ctx = escopo(page)

    if get_versao() >= 4:
        ctx.locator("button[name='submitFinish']").wait_for(state="visible")

    is_v3 = get_versao() == 3
    is_ja_selecionado = material_ja_selecionado(ctx, material)

    if not is_ja_selecionado:
        if is_v3:
            campo_almoxarifado = ctx.locator("input[name='almoxarifado']")
            if campo_almoxarifado.is_disabled():
                ctx.locator("button[name='submitNew']").click()
                aguardar_ajax_global(page)
        else:
            ctx.locator("button[name='submitNew']").click()
            aguardar_ajax_global(page)

        preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado)
        if not is_v3:
            expect(ctx.locator("input[name='ug']")).to_have_value(re.compile(r".+"))
        preencher_campo(ctx, "input[name='material']", material)
        aguardar_ajax_global(page)

    tabela = ctx.locator("table.tabela")
    linhas = tabela.locator("tbody tr")

    if get_versao() >= 4:
        try:
            linhas.first.wait_for(state="visible", timeout=1_000)
        except Exception:
            pass

    count = linhas.count()
    if count > 0:
        for i in range(count):
            texto = linhas.nth(i).locator("td").nth(2).locator("input").input_value()
            if " - " in texto:
                partes = texto.split(" - ", 1)
                codigo = partes[0].strip()
                descricao = partes[1].strip()
                if endereco["codigo"] == codigo or endereco["descricao"] == descricao:
                    return True
            else:
                if endereco["codigo"] in texto or endereco["descricao"] in texto:
                    return True

    return False


def material_ja_selecionado(ctx, material: str) -> bool:
    material_input = ctx.locator("input[name='material']")
    if not material_input.is_visible():
        return False
    val = material_input.input_value()
    return material.lower().strip() in val.lower().strip()


