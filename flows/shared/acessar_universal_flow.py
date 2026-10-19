from collections.abc import Callable, Sequence

from loguru import logger
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, expect

from utils.versao import get_versao
from utils.waits import (
    aguardar_ajax_global,
    clicar_home_com_retry,
    clicar_menu_com_retry,
)

MAX_TENTATIVAS = 2


class _CaminhoIndisponivel(Exception):
    """Um item do caminho não ficou visível dentro do tempo de espera."""


def acessar_universal(
    page: Page,
    destino: str,
    caminho_v3: Sequence[str],
    caminho_v4: Sequence[str],
    *,
    opcional: bool = False,
) -> bool:
    """Navega pelos menus do ASI com até duas tentativas.

    Args:
        page: Página Playwright usada para navegar e aguardar o AJAX.
        destino: Nome da página para os logs e a mensagem de falha.
        caminho_v3: Seletores dos itens de menu, na ordem de clique, para a v3.
        caminho_v4: Seletores dos itens de menu, na ordem de clique, para a v4+.
        opcional: Se True, devolve False quando um item do menu não aparece.

    Returns:
        True quando percorre todo o caminho; False apenas para menu opcional
        indisponível após as duas tentativas.

    Raises:
        RuntimeError: Quando a navegação obrigatória falha, ou quando há erro
        ao abrir ou clicar no menu mesmo em uma navegação opcional.
    """
    logger.info("Iniciou navegação para página: {}.", destino)
    aguardar_ajax_global(page)
    if get_versao() >= 4:
        encontrou = _navegar_v4(page, caminho_v4, destino, opcional)
    else:
        encontrou = _navegar_v3(page, caminho_v3, destino, opcional)
    if encontrou:
        logger.info("Finalizou navegação para página: {}.", destino)
    return encontrou


def _percorrer_caminho(page: Page, caminho: Sequence[str]) -> None:
    for step in caminho:
        locator = page.locator(step)
        try:
            expect(locator).to_be_visible()
        except AssertionError as erro:
            raise _CaminhoIndisponivel from erro
        locator.click()
        aguardar_ajax_global(page)


def _navegar_com_retry(
    page: Page,
    caminho: Sequence[str],
    preparar: Callable[[], None],
    destino: str,
    opcional: bool,
) -> bool:
    ultimo_erro: Exception | None = None
    erro_operacional: Exception | None = None
    for tentativa in range(MAX_TENTATIVAS):
        try:
            preparar()
            aguardar_ajax_global(page)
            _percorrer_caminho(page, caminho)
            return True
        except (_CaminhoIndisponivel, PlaywrightError, RuntimeError) as erro:
            ultimo_erro = erro
            if not isinstance(erro, _CaminhoIndisponivel):
                erro_operacional = erro
            if tentativa < MAX_TENTATIVAS - 1:
                logger.warning("Navegação falhou. Tentando novamente...")
    if opcional and erro_operacional is None:
        logger.warning("Falha ao concluir navegação após {} tentativas", MAX_TENTATIVAS)
        return False
    raise RuntimeError(
        f"Falha ao acessar '{destino}' após {MAX_TENTATIVAS} tentativas."
    ) from (erro_operacional or ultimo_erro)


def _navegar_v3(page: Page, caminho: Sequence[str], destino: str, opcional: bool) -> bool:
    def preparar() -> None:
        clicar_menu_com_retry(page)
    encontrou = _navegar_com_retry(page, caminho, preparar, destino, opcional)
    return encontrou


def _navegar_v4(page: Page, caminho: Sequence[str], destino: str, opcional: bool) -> bool:
    def preparar() -> None:
        clicar_home_com_retry(page)
    encontrou = _navegar_com_retry(page, caminho, preparar, destino, opcional)
    return encontrou
