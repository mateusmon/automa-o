from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_recebimento(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de recebimento de transferência entre almoxarifados.")

    ctx = escopo(page)
    encontrado = _selecionar(ctx, page, almoxarifado)

    if encontrado:
        logger.info("Finalizou seleção de recebimento de transferência entre almoxarifados.")

    return encontrado


def _selecionar(ctx, page: Page, almoxarifado: dict[str, str]) -> bool:
    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").filter(has_text=almoxarifado["nome"])
    ).first

    try:
        linha.wait_for(state="visible", timeout=2_000)
    except Exception:
        pass

    if linha.count() == 0:
        logger.info("Nenhuma transferência encontrada para o almoxarifado '{}'.", almoxarifado["sigla"])
        return False

    logger.info("Selecionando recebimento de transferência para o almoxarifado '{}'.", almoxarifado["sigla"])
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    return True
