from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def editar_material(page: Page, bem: dict[str, str]) -> bool:

    logger.info("Iniciou edição de entrada para o bem '{}'.", bem["nome"])

    ctx = escopo(page)

    ctx.get_by_role("button", name="Materiais").click()
    aguardar_ajax_global(page)

    expect(ctx.get_by_role("heading", name="Itens da entrada")).to_be_visible()
     
    campo_valor_total = ctx.locator("input[name='valor-1-6']")
    campo_valor_nf = ctx.locator("input[name='vlTotalNF']")

    if campo_valor_total.is_disabled():
        logger.info("Campo de valor do material está desabilitado.")
        return False

    valor_limpo = campo_valor_total.input_value().replace(".", "").replace(",", ".")

    if campo_valor_total.input_value() == bem["preco_unitario"]:
        # Valor 10% maior
        valor_alterado = float(valor_limpo) * 1.1
        valor_str = f"{valor_alterado:.2f}".replace(".", ",")
    else:
        valor_str = bem["preco_unitario"]
    logger.info("Alterando valor do material de '{}' para '{}'.", campo_valor_total.input_value(), valor_str)
    campo_valor_total.fill(valor_str)
    campo_valor_nf.click()
    aguardar_ajax_global(page)
    total_informado = ctx.locator("input[name='valorDigitado']").input_value()
    campo_valor_nf.fill(total_informado)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    if ctx.locator("button[name='submitBack']").is_enabled():
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)

    logger.info("Finalizou edição de entrada para o bem '{}'.", bem["nome"])
    return True
