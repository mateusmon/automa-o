from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def selecionar_ug(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou seleção da UG '{}' para recebimento da devolução de materiais.", ug["nome"])

    ctx = escopo(page)
    # Foi necessário utilizar `select_option` com o `label`, pois alguns clientes
    # possuem UGs com nomes semelhantes. O `select_tipo` acabava selecionando a UG
    # incorreta por fazer uma correspondência parcial. Dessa forma, a seleção é
    # realizada pelo nome exato da UG.

    # select_tipo(ctx, "ug", ug["nome"])

    logger.info("Selecionando UG '{}'.", ug["nome"])
    ctx.locator("select[name='ug']").select_option(label=ug["nome"])

    logger.info("Finalizou seleção da UG '{}'.", ug["nome"])
