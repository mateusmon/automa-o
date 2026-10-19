from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def escolher_tipo_bem(page: Page, tipo_bem: str | None = None) -> None:
    """
    Seleciona o Tipo de Bem por correspondência parcial (case-insensitive)
    do texto visível das opções. Se `tipo_bem` for None/vazio, mantém o
    valor padrão da interface.
    """
    logger.info("Iniciou escolha do Tipo de Bem '{}'.", tipo_bem)

    ctx = escopo(page)
    _selecionar(ctx, page, tipo_bem)

    logger.info("Finalizou escolha do Tipo de Bem '{}'.", tipo_bem)


def _selecionar(ctx, page: Page, tipo_bem: str | None) -> None:
    if not tipo_bem:
        logger.info("Tipo de Bem padrão mantido.")
        return

    aguardar_ajax_global(page)
    alvo = tipo_bem.upper().strip()
    select = ctx.locator("select[name='tipoBem']")
    select.wait_for(state="visible")
    options = select.locator("option")

    for i in range(options.count()):
        option = options.nth(i)
        texto = option.inner_text().upper()

        if alvo in texto:
            select.select_option(value=option.get_attribute("value"))
            aguardar_ajax_global(page)
            logger.info("Tipo de Bem selecionado: {}", texto)
            return

    raise ValueError(f"Tipo de Bem não encontrado no select: {tipo_bem}")
