from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def escolher_finalidade(page: Page, finalidade: str | None = None) -> None:
    """
    Seleciona a finalidade de entrada no campo "Finalidade"
    com base em uma correspondência parcial do texto visível das opções.

    Estratégia:
        - Percorre dinamicamente todas as opções do <select>.
        - Seleciona a primeira opção cujo texto contenha o valor informado.
        - A comparação é case-insensitive.
        - Se nenhum tipo for informado, mantém o valor padrão da interface.

    Parâmetros:
        page (Page):
            Instância da página do Playwright.

        finalidade (str | None):
            Texto parcial da finalidade desejada.
            Exemplo:
                "Consumo"  -> seleciona "Consumo Imediato"
                "Evento"   -> seleciona "Evento"

            Se None ou vazio, o valor padrão permanece selecionado.

    Exceções:
        ValueError:
            Caso o texto informado não corresponda a nenhuma opção disponível.
    """
    logger.info("Iniciou escolha da finalidade '{}'.", finalidade)

    ctx = escopo(page)
    _selecionar(ctx, page, finalidade)

    logger.info("Finalizou escolha de finalidade '{}'.", finalidade)


def _selecionar(ctx, page: Page, finalidade: str | None) -> None:
    if not finalidade:
        logger.info("Finalidade padrão mantida.")
        return

    finalidade = finalidade.upper().strip()
    logger.info("Selecionando finalidade: '{}'.", finalidade)
    select = ctx.locator('select[name="finalidade"]')
    expect(select).to_be_visible()
    select.locator("option").first.wait_for(state="attached", timeout=10000)
    options = select.locator("option")
    count = options.count()

    for i in range(count):
        option = options.nth(i)
        texto = option.inner_text().upper()

        if finalidade in texto:
            value = option.get_attribute("value")
            select.select_option(value=value)
            aguardar_ajax_global(page)
            logger.info("Finalidade selecionada: '{}'", texto)
            return

    raise ValueError(f"Finalidade não encontrada no select: {finalidade}")
