from loguru import logger
from playwright.sync_api import expect, Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo, aguardar_ajax_global


def preencher_dados_gerais(page: Page, almoxarifado: dict[str, str], material: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de dados gerais.")

    nome_almoxarifado = almoxarifado["sigla"]
    nome_material = material["nome"]
    complemento_material = material["complemento"]
    nome_completo_material = f"{nome_material} {complemento_material}"

    ctx = escopo(page)

    # A consulta PRECISA ser feita nessa ordem, ou ela vai falhar se não houver materiais
    logger.info("Preenchendo nome do material '{}'.", nome_completo_material)
    preencher_campo(ctx, 'input[name="cdBemServico"]', nome_completo_material)
    clicar_com_ajax(ctx, "button[name='submitTabMaterial']")
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", nome_almoxarifado)
    preencher_campo(ctx, 'input[name="cdAlmoxarifado"]', nome_almoxarifado)
    expect(ctx.locator('span[name="classificacao"]')).not_to_have_text("", timeout=10_000)

    qtd_estoque = ctx.locator("span[name='qtEstoqueTotal']").inner_text().strip()

    if qtd_estoque == "0":
        logger.info("O material '{}' não possui estoque no almoxarifado '{}'.", nome_completo_material, almoxarifado["nome"])
        return False

    logger.info("Finalizou preenchimento de dados gerais.")
    return True
