from loguru import logger
from playwright.sync_api import Page

from utils.versao import get_versao
from utils.waits import clicar_com_ajax


def logout(page: Page) -> None:
    logger.info("Iniciou logout.")

    if get_versao() >= 4:
        clicar_com_ajax(page, "button[title='Sair'].btn-toolbar:visible")
    else:
        clicar_com_ajax(page, "#appLogout:visible")

    logger.info("Finalizou logout.")
