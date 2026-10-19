from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def validar_botoes_remover(page: Page) -> None:
    logger.info("Iniciou validação dos botões de remover.")

    ctx = escopo(page)

    linhas_selecionadas = ctx.locator("table[name='itenstab'] tbody tr")

    if linhas_selecionadas.count() > 0:
        linhas_selecionadas.first.locator("button[name='submitRemove']").click()
        aguardar_ajax_global(page)

    if linhas_selecionadas.count() > 0:
            ctx.get_by_role("button", name="Retirar todos").click()
            aguardar_ajax_global(page)

    expect(linhas_selecionadas).to_have_count(0)
    expect(ctx.get_by_role("button", name="Retirar todos")).to_be_disabled()

    logger.success("Finalizou validação dos botões de remover.")