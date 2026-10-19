from loguru import logger
from playwright.sync_api import Page


def esperar_visualizacao(page: Page, tempo) -> None:
    logger.info("Esperando visualização do usuário.")

    page.wait_for_timeout(tempo)
    
    logger.info("Finalizou espera de visualização do usuário.")
