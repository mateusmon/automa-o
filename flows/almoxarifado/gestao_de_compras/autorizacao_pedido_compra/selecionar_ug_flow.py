from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, select_tipo


def selecionar_ug(page: Page, ug_data: dict) -> None:
    logger.info("Selecionando UG {}.", ug_data["nome"])

    ctx = escopo(page)

    select_tipo(ctx, 'cmbUgs', ug_data["nome"])
    aguardar_ajax_global(page)

    logger.info("Seleção de Unidade Gestora '{}' finalizada.", ug_data["nome"])
