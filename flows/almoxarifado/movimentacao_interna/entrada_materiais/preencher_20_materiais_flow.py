from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    preencher_campo,
)


def preencher_20_materiais(page: Page, materiais: list[dict], quantidade: str = "1") -> None:
    logger.info("Iniciando preenchimento da aba 'Materiais' com 20 materiais.")

    ctx = escopo(page)
    _preencher(ctx, page, materiais, quantidade)

    logger.info("Finalizando preenchimento da aba 'Materiais' com 20 materiais.")


def _preencher(ctx, page: Page, materiais: list[dict], quantidade: str) -> None:
    ctx.get_by_role("button", name="Materiais").click()
    expect(ctx.get_by_role("heading", name="Totais")).to_be_visible()
    aguardar_ajax_global(page)
    valor_total=0
    for step in range(len(materiais)):
        material = materiais[step]
        nome_completo_material = f"{material['nome']} {material['complemento']}"

        if ctx.locator("input[name='precoMedioCkb']").is_checked():
            ctx.locator("input[name='precoMedioCkb']").uncheck()

        logger.info("Preenchendo material {}: '{}'.", step + 1, nome_completo_material)
        preencher_campo(ctx, 'input[name="cdBemServico-1-3"]', nome_completo_material)

        logger.info("Preenchendo quantidade do material {}: '{}'.", step + 1, quantidade)
        quantidade_input = ctx.locator('input[name="qtNotaRecItem-2-5"]')
        quantidade_input.select_text()
        quantidade_input.type(quantidade, delay=50)

        valor_total_item = f"{(float(material['preco_unitario'].replace(',', '.')) * int(quantidade)):.2f}".replace(".", ",")
        valor_total += float(material['preco_unitario'].replace(',', '.')) * int(quantidade)

        valor_input = ctx.locator('input[name="vlNotaRecItem-2-6"]')
        # para entrada tipo devolução ele não está habilitado
        if valor_input.is_enabled():
            logger.info("Preenchendo valor do material {}: '{}'.", step + 1, valor_total_item)
            valor_input.clear()
            valor_input.type(valor_total_item, delay=50)

    valor_total_formatado = f"{(valor_total):.2f}".replace(".", ",")
    valor_total_input = ctx.locator("#vlTotalInformado")
    valor_total_input.click()
    logger.info("Preenchendo valor total: '{}'.", valor_total_formatado)
    valor_total_input.type(valor_total_formatado, delay=50)
    valor_total_input.press("Tab")
    