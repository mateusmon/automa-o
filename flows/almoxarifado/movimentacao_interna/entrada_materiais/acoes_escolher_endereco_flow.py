from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def acoes_escolher_endereco(page: Page, material: dict[str, str]) -> None:
    logger.info("Escolhendo o endereço para o material '{}'.", material["nome"])

    ctx = escopo(page)

    nome_completo_material = f"{material['nome']} {material['complemento']}"

    linha = ctx.locator("table.tabela.material tbody tr").filter(
        has=ctx.locator(f"input[name^='cdBemServico'][value*='{nome_completo_material}']")
    ).first

    botao_acoes = linha.locator("button[name^='edit-cdBemServico']")
    clicar_com_ajax(ctx, botao_acoes)
    aguardar_ajax_global(page)

    select = ctx.locator("select[name='endBSPossivel']")
    options = select.locator("option")

    for i in range(options.count()):
        option = options.nth(i)
        label = option.inner_text()

        if material["codigo_endereco"] in label:
            valor = option.get_attribute("value")
            logger.info("Escolhendo o endereço '{}' para o material '{}'.", label, nome_completo_material)
            select.select_option(value=valor)
            
    clicar_com_ajax(ctx, "button[name='submitBack']")
    clicar_com_ajax(ctx, "button[name='submitTabOrigem']")

    logger.info("Endereço escolhido para o material '{}'.", material["nome"])
