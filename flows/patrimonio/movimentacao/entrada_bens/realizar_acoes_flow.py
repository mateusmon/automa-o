from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    esperar_sucesso_ou_erro,
    preencher_campos_erros,
)


def realizar_acoes(page: Page) -> None:
    logger.info("Iniciou realização de ações.")

    ctx = escopo(page)

    ctx.locator('button[name="edit-bemServOrgao-1-8"]').click()
    # Aba de bens
    ctx.locator("button[name='submitTabBensFisico']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='geraNumeroDisponivel-cdBemPerm-1-1-3']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='geraNumeroInformado-cdBemPerm-1-1-3']").click()
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Retornar").click()
    aguardar_ajax_global(page)

    # Às vezes a aplicação gera um número usado. Assim ele clica de novo para gerar outro número
    vezes = 0

    while ctx.locator(".alert-danger").is_visible() and vezes < 31:
        ctx.get_by_role("button", name="Gera o último número disponí").click()
        aguardar_ajax_global(page)
        ctx.get_by_role("button", name="Retornar").click()
        aguardar_ajax_global(page)
        vezes += 1

    clicar_com_ajax(ctx, "button[name='submitFinish']")
    preencher_campos_erros(ctx)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou realização de ações .")
