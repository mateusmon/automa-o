from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_itens_completo(page: Page, material: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de itens da devolução.")

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.get_by_role("button", name="Itens").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitPurgeLines1']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    ctx.fill("input[name='cdBemServico-1-3']", nome_completo_material)
    ctx.click("button[name='lookup-cdBemServico-1-3']")
    aguardar_ajax_global(page)

    if ctx.locator(".alert-warning").count() > 0:
        logger.info(
            "Não foi possível realizar a devolução pelo seguinte motivo:",
            ctx.locator(".alert-warning").inner_text(),
        )
        logger.info("Pulando teste.")
        return True

    valor_str = ctx.locator("input[name='qtNotaRecItemMax-2-5']").input_value()
    valor_limpo = float(valor_str.replace(".", "").replace(",", "."))
    valor_numerico = int(valor_limpo / 2) if valor_limpo >= 2 else 1
    quantidade_calculada = str(valor_numerico)

    ctx.locator("input[name='qtNotaRecItem-2-7']").fill(quantidade_calculada)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de itens da devolução.")
    return False
