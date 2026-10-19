from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_natureza(page: Page) -> str:
    logger.info("Iniciou seleção de natureza do material.")

    ctx = escopo(page)

    natureza = ctx.get_by_role("cell", name="ESTOCÁVEL").inner_text()
    options = ctx.locator("select[name='cdTpUsoEstoque'] option")

    for i in range(options.count()):
        option = options.nth(i)
        texto = option.inner_text()
        valor = option.get_attribute("value")

        if valor != "-1" and texto != natureza:
            logger.info("Selecionando natureza do material '{}'.", texto)
            ctx.select_option("select[name='cdTpUsoEstoque']", index=i)
            break

    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de natureza.")
    return natureza
