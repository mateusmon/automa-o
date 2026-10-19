"""Leitura do nome do usuário autenticado no cabeçalho do ASI."""

from loguru import logger
from playwright.sync_api import Locator, Page

from utils.versao import get_versao


def obter_nome_usuario_logado(page: Page, timeout: float = 15_000) -> str:
    """Retorna o nome exibido para o usuário autenticado no painel do cabeçalho.

    :param page: Página principal do ASI.
    :param timeout: Tempo máximo para o painel disponibilizar o nome.
    :return: Texto identificador do usuário, normalmente ``LOGIN - NOME``.
    :raises RuntimeError: Quando o painel não abre ou não apresenta um nome.
    """
    logger.info("Iniciou identificação do usuário logado.")

    candidatos = _localizar_candidatos(page)
    painel_aberto = False
    if not _esta_visivel(candidatos):
        _abrir_painel(page)
        painel_aberto = True
        candidatos = _localizar_candidatos(page)
        candidatos.first.wait_for(state="visible", timeout=timeout)

    page.wait_for_function(
        """
        () => Array.from(document.querySelectorAll('p.descUser')).some((item) => {
            const texto = (item.textContent || '').trim();
            return texto && !texto.endsWith(':');
        })
        """,
        timeout=timeout,
    )
    nome = _extrair_nome(candidatos)

    if painel_aberto:
        _fechar_painel(page)
    if not nome:
        raise RuntimeError(
            "Não foi possível identificar o usuário logado; a cópia de Perfis "
            "depende desse nome para localizar os registros de origem."
        )

    logger.info("Finalizou identificação do usuário logado como '{}'.", nome)
    return nome


def _localizar_candidatos(page: Page) -> Locator:
    """Localiza os textos apresentados no painel do usuário."""
    if get_versao() >= 4:
        return page.locator("p.descUser")

    candidatos_v3 = page.locator("#tplPanelUser p.descUser")
    if candidatos_v3.count() > 0:
        return candidatos_v3
    return page.locator("p.descUser")


def _abrir_painel(page: Page) -> None:
    """Abre o painel do usuário na versão ativa."""
    if get_versao() >= 4:
        page.get_by_title("Usuário").click()
        return
    page.locator("#centralHeaderUserName").click()


def _extrair_nome(candidatos: Locator) -> str:
    """Escolhe preferencialmente o texto no formato ``LOGIN - NOME``."""
    textos = [
        candidatos.nth(indice).inner_text().strip()
        for indice in range(candidatos.count())
    ]
    for texto in textos:
        if texto and not texto.endswith(":") and " - " in texto:
            return texto
    for texto in textos:
        if texto and not texto.endswith(":"):
            logger.warning(
                "Painel fora do formato 'LOGIN - NOME'; usando '{}'.", texto
            )
            return texto
    return ""


def _fechar_painel(page: Page) -> None:
    """Fecha o painel que foi aberto apenas para identificar o usuário."""
    try:
        if get_versao() >= 4:
            page.get_by_role("button", name="x").click()
            return

        botao = page.locator("#centralHeaderUserContentCloseButton")
        if botao.is_visible():
            botao.click()
            return
        page.keyboard.press("Escape")
    except Exception as erro:
        logger.debug("Não foi possível fechar o painel do usuário: {}", erro)


def _esta_visivel(locator: Locator) -> bool:
    """Consulta visibilidade sem deixar a detecção opcional interromper o teste."""
    try:
        return locator.first.is_visible()
    except Exception:
        return False
