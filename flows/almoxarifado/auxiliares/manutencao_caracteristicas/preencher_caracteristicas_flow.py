from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_caracteristicas(page: Page, caracteristica: str = "MARCA AUTOMATIZADA", conteudo: str = "ROMA") -> bool:
    logger.info("Preenchendo características.")

    ctx = escopo(page)

    try:
        logger.info("Preenchendo característica '{}'.", caracteristica)
        preencher_campo(ctx, "input[name='cdCaracteristica']", caracteristica)
    except Exception:
        logger.info("Nenhuma característica '{}' encontrada. Rode o teste de definição de características primeiro.", caracteristica)
        return True

    linhas = ctx.locator(".tabela tbody tr")

    if linhas.count() > 0:
        logger.info("Característica '{}' já preenchida.", caracteristica)
        return True
    
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)    

    logger.info("Preenchendo conteúdo '{}'.", conteudo)
    ctx.locator("input[name='nmCaractTab-1-4']").fill(conteudo)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Preenchimento de características finalizado.")
    return False
