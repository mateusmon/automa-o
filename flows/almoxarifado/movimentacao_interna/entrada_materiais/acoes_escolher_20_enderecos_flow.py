from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def acoes_escolher_20_enderecos(page: Page, materiais: dict) -> None:
    logger.info("Escolhendo o endereço.")

    ctx = escopo(page)
    _escolher_20_endereco(ctx, page, materiais)

    logger.info("Endereço escolhido com sucesso.")


def _escolher_20_endereco(ctx, page: Page, materiais: dict) -> None:
    for step in range(len(materiais)):
        material = materiais[step]
        nome_completo_material = f"{material['nome']} {material['complemento']}"

        linha = ctx.locator("table.tabela.material tbody tr").filter(
            has=ctx.locator(f"input[name^='cdBemServico'][value*='{nome_completo_material}']")
        ).first

        botao_acoes = linha.locator("button[name^='edit-cdBemServico']")
        botao_acoes.click()
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

        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)
