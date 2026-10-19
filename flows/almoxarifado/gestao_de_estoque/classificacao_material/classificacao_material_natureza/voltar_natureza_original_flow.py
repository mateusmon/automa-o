from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def voltar_natureza_original(page: Page, natureza: str) -> None:
    logger.info("Iniciou restauração da natureza original do material.")

    ctx = escopo(page)

    options = ctx.locator("select[name='cdTpUsoEstoque'] option")

    for i in range(options.count()):
        option = options.nth(i)
        texto = option.inner_text()
        valor = option.get_attribute("value")

        if valor != "-1" and texto == natureza:
            logger.info("Restaurando natureza do material '{}'.", texto)
            ctx.select_option("select[name='cdTpUsoEstoque']", index=i)
            break

    aguardar_ajax_global(page)

    ctx.locator("button[name='submitAdicionar']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou restauração da natureza original do material.")
