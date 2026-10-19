from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preencher_itens(page: Page, material: dict[str, str]) -> bool:
    logger.info(
        "Iniciou preenchimento de itens da devolução para o material {}.",
        material["nome"],
    )

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.get_by_role("button", name="Itens").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    ctx.fill("input[name='cdBemServico-1-3']", nome_completo_material)
    ctx.click("button[name='lookup-cdBemServico-1-3']")
    aguardar_ajax_global(page)

    if ctx.locator(".alert-warning").count() > 0:
        logger.info(
            "Não foi possível realizar a devolução pelo seguinte motivo:",
            ctx.locator(".alert-warning").inner_text(),
        )
        return True

    # Pega a quantidade maxima do item e preenche o campo Qtd com o valor
    quantidade_max = ctx.locator("input[name='qtNotaRecItemMax-2-5']").input_value()

    logger.info("Preenchendo quantidade máxima do item: '{}'.", quantidade_max)
    ctx.locator("input[name='qtNotaRecItem-2-7']").fill(quantidade_max)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de itens da devolução.")
    return False
