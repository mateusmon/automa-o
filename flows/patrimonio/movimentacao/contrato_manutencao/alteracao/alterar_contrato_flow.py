from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, proximo_nome


def alterar_contrato(page: Page) -> None:
    ctx = escopo(page)
    name_ug = ctx.locator("input[name='cdUg']").input_value()
    logger.info(
        "Iniciou alteração de contrato para a unidade gestora '{}'.",
        name_ug,
    )

    campo = ctx.locator("textarea[name='dsObjeto']")
    logger.info(
        "Alterando o campo 'Objeto' de '{}' para '{}'.",
        campo.input_value(),
        proximo_nome(campo.input_value()),
    )
    campo.fill(proximo_nome(campo.input_value()))
    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)

    logger.info(
        "Finalizou alteração de contrato para a unidade gestora '{}'.",
        name_ug,
    )
