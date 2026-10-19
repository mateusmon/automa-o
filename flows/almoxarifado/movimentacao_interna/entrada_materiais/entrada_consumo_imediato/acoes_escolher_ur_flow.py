from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, preencher_campo


def acoes_escolher_ur(page: Page, material: dict[str, str], ur: dict[str, str]) -> None:
    logger.info("Iniciou escolha de UR para o material '{}'.", material["nome"])

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"
    
    linha = ctx.locator("table.tabela.material tbody tr").filter(
        has=ctx.locator(f"input[name^='cdBemServico'][value*='{nome_completo_material}']")
    ).first

    botao_acoes = linha.locator("button[name^='edit-cdBemServico']")
    clicar_com_ajax(ctx, botao_acoes)
    aguardar_ajax_global(page)

    campo_ur = ctx.locator("input[name='ur']")

    if not campo_ur.is_visible():
        clicar_com_ajax(ctx, ctx.locator('button[name="submitBack"]'))
        aguardar_ajax_global(page)
        return

    logger.info("Preenchendo UR: '{}'.", ur["nome"])
    preencher_campo(ctx, "input[name='ur']", ur["nome"])

    clicar_com_ajax(ctx, 'button[name="submitBack"]')
    aguardar_ajax_global(page)

    logger.info("Finalizou escolha de UR.")
    