from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def excluir_observacao(page: Page, nome: str = "OBSERVAÇÃO AUTOMAÇÃO"):
    logger.info("Excluindo observação com o nome '{}'.", nome)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()

    aguardar_ajax_global(page)

    # Preencher o nome do tipo de documento
    logger.info("Preenchendo nome '{}'.", nome)
    ctx.locator("input[name='model-1']").click()
    ctx.locator("input[name='model-1']").fill(nome)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(
            has_text=nome
        )
    ).first

    if linha.count() == 0:
        logger.info("Nenhum documento com o nome '{}' encontrado.", nome)

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    # Aceitando caixa de diálogo para confirmação de exclusão
    ctx.once("dialog", lambda dialog: dialog.accept())
    ctx.locator("button[name='submitDelete']").click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
