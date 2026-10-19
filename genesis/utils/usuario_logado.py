import time

from loguru import logger
from playwright.sync_api import Page

from utils.versao_gen import get_versao


def obter_nome_usuario_logado(page: Page, timeout: float = 15_000) -> str:
    """
    Lê o nome do usuário atualmente logado no header da aplicação.

    """
    candidatos = _localizar_candidatos(page)
    clicou = False

    if not _esta_visivel(candidatos):
        _abrir_painel(page)
        clicou = True

        candidatos = _localizar_candidatos(page)

        try:
            candidatos.first.wait_for(state="visible", timeout=timeout)
        except Exception as e:
            raise RuntimeError(f"Painel do usuário logado não abriu: {e}") from e

    nome = _aguardar_nome(page, timeout=timeout)

    if clicou:
        _fechar_painel(page)

    if not nome:
        raise RuntimeError(
            "Não foi possível identificar o nome do usuário logado no painel do header. "
            "A cópia de perfis depende desse nome para consultar os perfis de origem."
        )

    logger.info("Usuário logado identificado como '{}'.", nome)
    return nome


def _localizar_candidatos(page: Page):
    """
    Retorna todos os parágrafos do painel do usuário.

    """
    if get_versao() >= 4:
        return page.locator("p.descUser")

    escopo_v3 = page.locator("#tplPanelUser p.descUser")
    if escopo_v3.count() > 0:
        return escopo_v3

    return page.locator("p.descUser")


def _abrir_painel(page: Page) -> None:
    if get_versao() >= 4:
        page.get_by_title("Usuário").click()
        return

    page.locator("#centralHeaderUserName").click()


def _aguardar_nome(page: Page, timeout: float) -> str:

    deadline = time.monotonic() + timeout / 1000

    while True:
        nome = _extrair_nome(_localizar_candidatos(page))
        if nome or time.monotonic() >= deadline:
            return nome
        page.wait_for_timeout(250)


def _extrair_nome(candidatos) -> str:

    total = candidatos.count()

    for num in range(total):
        texto = candidatos.nth(num).inner_text().strip()

        if not texto or texto.endswith(":"):
            continue

        if " - " not in texto:
            continue

        return texto

    for num in range(total):
        texto = candidatos.nth(num).inner_text().strip()
        if texto and not texto.endswith(":"):
            logger.warning(
                "Nenhum parágrafo do painel está no formato 'LOGIN - NOME'. "
                "Usando '{}' como nome do usuário logado.",
                texto,
            )
            return texto

    return ""


def _fechar_painel(page: Page) -> None:

    try:
        if get_versao() >= 4:
            page.get_by_role("button", name="x").click()
            return

        botao_v3 = page.locator("#centralHeaderUserContentCloseButton")
        if botao_v3.is_visible():
            botao_v3.click()
            return

        page.keyboard.press("Escape")
    except Exception as e:
        logger.debug("Não foi possível fechar o painel do usuário: {}", e)


def _esta_visivel(locator) -> bool:

    try:
        return locator.first.is_visible()
    except Exception:
        return False