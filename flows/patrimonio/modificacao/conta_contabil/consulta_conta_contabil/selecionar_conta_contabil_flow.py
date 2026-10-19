from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_conta_contabil(page: Page, bem: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de modificação de conta contábil.")

    ctx = escopo(page)
    nome_completo_bem = f"{bem['nome']} {bem['complemento']}"

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(2).filter(has_text=nome_completo_bem)
    ).first

    if linha.count() == 0:
        logger.info("Nenhuma modificação de conta contábil encontrada para o material '{}'.", nome_completo_bem)
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de modificação de conta contábil.")
    return True
