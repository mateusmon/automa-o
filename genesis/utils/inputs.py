from typing import Literal

from loguru import logger
from playwright.sync_api import Locator, Page, expect
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo

ResultadoClique = Literal[0, "alt_erro", "erro"]


def clicar_botao_com_retry(
    page: Page,
    btn_locator: str | Locator,
    locator_elemento_sucesso: str,
    locator_elemento_erro_alt: str | None = None,
    tentativas: int = 5,
) -> ResultadoClique:
    """
    Clica no botão, aguardando um elemento de sucesso ou de erro ficar visível.
    Tenta novamente se o clique não surtir efeito dentro do timeout.

    Algumas páginas renderizam o elemento de sucesso junto com o de erro
    alternativo ao mesmo tempo — nesse caso não é erro. Só é considerado erro
    quando o elemento de sucesso NÃO está visível.

    Returns:
        0 se o elemento de sucesso está visível (mesmo que o
        alternativo também esteja), "alt_erro" se apenas o elemento de erro
        alternativo ficou visível, ou "erro" se foi o elemento de erro padrão.
    """
    ctx = escopo(page)
    botao = btn_locator if isinstance(btn_locator, Locator) else ctx.locator(btn_locator)
    sucesso = ctx.locator(locator_elemento_sucesso).first
    erro = ctx.locator("div[name='divErrorMsg']").first
    alt_erro = ctx.locator(locator_elemento_erro_alt).first if locator_elemento_erro_alt is not None else None
    condicao_espera = sucesso.or_(erro) if alt_erro is None else sucesso.or_(erro).or_(alt_erro)
    condicao_espera = condicao_espera.first

    for tentativa in range(tentativas):
        botao.scroll_into_view_if_needed()
        botao.click()
        aguardar_ajax_global(page)

        try:
            expect(condicao_espera).to_be_visible(timeout=8_000)
            if sucesso.is_visible():
                return 0
            if alt_erro is not None and alt_erro.is_visible():
                return "alt_erro"
            return "erro"
        except AssertionError:
            logger.warning("Clique no botão não surtiu efeito. Tentativa {}/{}.", tentativa + 1, tentativas)
            page.wait_for_timeout(1_000)

    raise RuntimeError("Falha ao clicar no botão após várias tentativas.")