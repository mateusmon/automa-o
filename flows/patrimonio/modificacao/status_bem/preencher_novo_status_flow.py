from unicodedata import category, normalize

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, select_tipo


def preencher_novo_status(page: Page, novo_status: str) -> str:
    logger.info("Preenchendo novo status {}.", novo_status)

    ctx = escopo(page)

    status_origem = ctx.locator("td[name='cdStatusO-1-6']").inner_text()
    status_origem = status_origem.split(" - ", 1)[1]
    status_origem = ''.join(c for c in normalize('NFD', status_origem) if category(c) != 'Mn')

    novo_status = ''.join(c for c in normalize('NFD', novo_status) if category(c) != 'Mn')
    
    if novo_status == status_origem:
        select_tipo(ctx, "cdStatusD", "INDISPONÍVEL")
        aguardar_ajax_global(page)
    else:
        select_tipo(ctx, "cdStatusD", novo_status)
        aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Novo status preenchido com sucesso {}.", novo_status)
    return status_origem
