from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, clicar_com_ajax


def preencher_bens_transferir(page: Page, ul_padrao: dict[str, str], material: dict[str, str]) -> bool:
    logger.info("Iniciou o preenchimento dos bens.")

    ctx = escopo(page)
    
    ctx.locator("button[name='submitTabItens']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)
    
    preencher_campo(ctx, "input[name='model-7']", ul_padrao["sigla"])
    aguardar_ajax_global(page)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitSearch']"))

    try:
        ctx.locator("button[name='submitAddPage']").wait_for(state="visible", timeout=2_000)
    except Exception:
        pass

    # Caso especial: sistema pulou a listagem por haver somente um bem disponível.
    # Volta para a tabela e seleciona o único registro presente.
    if not ctx.locator("button[name='submitAddPage']").is_visible():
        # Verificando se é o item certo que apareceu
        if ctx.locator(f"text={material['nome']} {material['complemento']}").count() >= 1:
            ctx.locator("button[name='submitBack']").click()
            aguardar_ajax_global(page)
            (
                ctx.locator("table.tabela").first
                .locator("tbody tr").first
                .locator("button[name='submitUse']")
                .click()
            )
            aguardar_ajax_global(page)
            logger.info("Finalizou o preenchimento dos bens.")
            return True
        return False

    aguardar_ajax_global(page)
    rows = ctx.locator("table.tabela").first.locator("tbody tr")
    linha = rows.filter(has_text=f"{material['nome']} {material['complemento']}").first

    if linha.count() == 0:
        logger.info("Bem não encontrado na UL de sigla {}.", ul_padrao["sigla"])
        logger.info(
            "Dica: O bem provavelmente está localizado na UL de estoque. "
            "Faça primeiramente uma transferência interna, e depois rode o "
            "teste de transferência interna temporária."
        )
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    logger.info("Finalizou o preenchimento dos bens.")
    return True
