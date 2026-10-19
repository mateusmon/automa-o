from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_unidade_medida(page: Page, unidade_medida: dict) -> None:
    """
    Abre a Consulta de Unidade de Medida e filtra pela Sigla (`model-2`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    Filtra pela Sigla (não pela Descrição, `model-1`) porque o campo `dsUm` tem maxlength
    e a Descrição é truncada no banco (o " CR" final some), então a Descrição completa do
    blueprint não casaria. A Sigla ("UMC") é curta e íntegra.

    :param unidade_medida: dict do blueprint (usa a chave `sigla`).
    """
    logger.info("Iniciou consulta de Unidade de Medida.")

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-2']").fill(unidade_medida["sigla"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Unidade de Medida.")
