from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def atender_requisicao(page: Page, material: dict[str, str]) -> None:
    logger.info(
        "Iniciou atendimento de transferência do material '{}'.", (material["nome"])
    )

    ctx = escopo(page)
    _atender(ctx, page, material)

    logger.info("Finalizou atendimento de transferência.")


def _atender(ctx, page: Page, material: dict[str, str]) -> None:
    linha = ctx.locator(
        'tr[model="model-0"]',
        has=ctx.locator('td[name^="bemServico"]', has_text=material["nome"]),
    )

    linha.wait_for(state="visible")
    logger.info("Atendendo transferência do material '{}'.", (material["nome"]))
    if ctx.locator("input[name='dtConfirmada']").is_enabled():
        data_almox = obter_data_almoxarifado(page, "DDMMYYYY")
        ctx.locator("input[name='dtConfirmada']").clear()
        ctx.locator("input[name='dtConfirmada']").press_sequentially(
            data_almox, delay=50
        )

    linha.locator('input[name^="qtAtendido"]').type("1", delay=50)
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
