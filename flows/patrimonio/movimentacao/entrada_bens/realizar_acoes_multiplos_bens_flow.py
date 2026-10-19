from loguru import logger
from playwright.sync_api import expect, Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def realizar_acoes_multiplos_bens(page: Page, total_itens: int) -> None:
    """
    Executa a etapa de ações físicas (geração de número patrimonial/tombamento)
    para cada um dos bens inseridos na Entrada de Bens do Patrimônio.

    Após gerar os números patrimoniais para todos os itens, confirma a operação.
    """
    logger.info("Iniciou realização de ações para {} bens.", total_itens)

    ctx = escopo(page)

    for i in range(1, total_itens + 1):
        logger.info("Gerando número patrimonial para o bem {}/{}", i, total_itens)

        seletor_btn_edit = f'button[name="edit-bemServOrgao-{i}-8"]'
        if not ctx.locator(seletor_btn_edit).is_visible():
            seletor_btn_edit = f'button[name^="edit-bemServOrgao-{i}-"]'

        btn_edit = ctx.locator(seletor_btn_edit)
        clicar_com_ajax(ctx, btn_edit)

        # Aba de bens físicos
        ctx.locator("button[name='submitTabBensFisico']").click()
        aguardar_ajax_global(page)

        ctx.get_by_role("button", name="Gera o último número disponí").click()
        aguardar_ajax_global(page)

        ctx.get_by_role("button", name="Retornar").click()
        aguardar_ajax_global(page)

        # Caso a aplicação gere um número já utilizado, tenta gerar outro
        vezes = 0
        while ctx.locator(".alert-danger").is_visible() and vezes < 31:
            ctx.get_by_role("button", name="Gera o último número disponí").click()
            aguardar_ajax_global(page)
            ctx.get_by_role("button", name="Retornar").click()
            aguardar_ajax_global(page)
            vezes += 1

    # Confirma a entrada de todos os bens
    logger.info("Confirmando a entrada de bens.")
    clicar_com_ajax(ctx, "button[name='submitFinish']")
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou realização de ações para {} bens com sucesso.", total_itens)

    expect(
            page.get_by_role("heading", name="Relatórios disponíveis")
            .or_(page.get_by_role("heading", name="Movimentação - Entrada de Bens"))
        ).to_be_visible()
