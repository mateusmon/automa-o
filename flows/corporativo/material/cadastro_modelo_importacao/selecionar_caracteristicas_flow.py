from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def selecionar_caracteristicas(page: Page) -> None:
    """
    Anexa a característica da primeira linha do resultado e confirma o cadastro. Cenário A.
    É o último flow da sequência de criação, portanto faz o submit (`submitFinish`) e
    aguarda o alerta de sucesso/erro (levanta em erro → passou = `.alert-success` real).

    Escopa-se ao Anexar da primeira linha (`tr:first-child`) — o grid ext replica linhas
    ocultas de medição, então `.first` simples casaria um botão não-clicável. Não se prende
    a um nome, pois o catálogo de características varia por cliente.
    """
    logger.info("Iniciou seleção de características.")

    ctx = escopo(page)

    try:
        btn_anexar = ctx.locator("table[name='paginationTable'] tbody tr:first-child button[name='submitUse']")
        expect(btn_anexar).to_be_visible()
        btn_anexar.click()
        aguardar_ajax_global(page)
    except AssertionError:
        logger.warning("Não existem características para serem anexadas")
        return False

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou seleção de características.")
    return True
