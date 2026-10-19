from collections.abc import Callable, Sequence

from loguru import logger
from playwright.sync_api import Page, expect

from utils.espera import (
    aguardar_ajax_global,
    clicar_home_com_retry,
    clicar_menu_com_retry,
)
from utils.versao_gen import get_versao

MAX_TENTATIVAS = 2

def acessar_universal(page: Page, destino: str, caminho_v3: Sequence[str], caminho_v4: Sequence[str]) -> bool:
    logger.info("Iniciou navegação para página: {}.", destino)
    aguardar_ajax_global(page)
    if get_versao() >= 4:
        encontrou = _navegar_v4(page, caminho_v4)
    else:
        encontrou = _navegar_v3(page, caminho_v3)
    logger.info("Finalizou navegação para página: {}.", destino)
    return encontrou


def _percorrer_caminho(page: Page, caminho: Sequence[str]) -> bool:
    for step in caminho:
        locator = page.locator(step)
        try:
            expect(locator).to_be_visible(timeout=10000)
        except Exception as e:
            logger.info("Elemento '{}' não encontrado. Erro: {}", step, e)
            return False
        locator.click()
        aguardar_ajax_global(page)
    return True


def _navegar_com_retry(page: Page, caminho: Sequence[str], preparar: Callable[[], None]) -> bool:
    encontrou = False
    for tentativa in range(MAX_TENTATIVAS):
        try:
            preparar()
            aguardar_ajax_global(page)
            encontrou = _percorrer_caminho(page, caminho)
            if encontrou: return encontrou
        except Exception:
            logger.warning(
                "Navegação falhou na tentativa {}. Tentando novamente.", tentativa+1
            )
    logger.warning("Falha ao concluir navegação após {} tentativas", MAX_TENTATIVAS)
    return encontrou


def _navegar_v3(page: Page, caminho: Sequence[str]) -> bool:
    def preparar() -> None:
        clicar_menu_com_retry(page)
    encontrou = _navegar_com_retry(page, caminho, preparar=preparar)
    return encontrou


def _navegar_v4(page: Page, caminho: Sequence[str]) -> bool:
    def preparar() -> None:
        clicar_home_com_retry(page)
    encontrou = _navegar_com_retry(page, caminho, preparar=preparar)
    return encontrou
