from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import preencher_campo


def verificar_calendario(page: Page, ur_data: dict[str, str]) -> bool:
    ur = ur_data["nome"]

    ctx = escopo(page)

    logger.info("Iniciou verificação de calendário da UR '{}'.", ur_data)

    preencher_campo(ctx, "input[name='ur']", ur)
    primeira_linha = ctx.locator("table.tabela tbody tr").first
    primeiro_campo = primeira_linha.locator("input[type='text']").first

    try:
        expect(primeiro_campo).not_to_have_value("", timeout=1_000)
        logger.info("Calendário da UR '{}' já preenchido.", ur_data)
        logger.info("Finalizou verificação de calendário.")
        return True
    except AssertionError:
        pass

    logger.info("Finalizou verificação de calendário da UR '{}'.", ur_data)
    return False
