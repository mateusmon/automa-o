from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo, proximo_nome


def alterar_caracteristicas(page: Page, caracteristica: str = "MARCA AUTOMATIZADA") -> bool:
    logger.info("Iniciou alteração de características.")

    ctx = escopo(page)

    try:
        logger.info("Preenchendo característica '{}'.", caracteristica)
        preencher_campo(ctx, "input[name='cdCaracteristica']", caracteristica)
    except Exception:
        logger.info("Nenhuma característica '{}' encontrada. Rode o teste de definição de características primeiro.", caracteristica)
        return True

    linhas = ctx.locator(".tabela tbody tr")

    if linhas.count() == 0:
        logger.info("Nenhuma característica encontrada. Rode o teste de manutenção de características primeiro.")
        return True
    
    valor_atual = ctx.locator("input[name='nmCaractTab-1-4']").input_value()
    novo_valor = proximo_nome(valor_atual)

    logger.info("Alterando valor da característica: '{}' -> '{}'.", valor_atual, novo_valor)

    ctx.locator("input[name='nmCaractTab-1-4']").fill(novo_valor)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Preenchimento de características finalizado.")
    return False
