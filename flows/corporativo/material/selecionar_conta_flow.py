import random

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_conta(page: Page) -> bool:
    """
    Abre o lookup da Conta contábil e escolhe uma linha aleatória, evitando contas
    de material HOSPITALAR/ODONTOLOGICO (que exigem regras específicas). Cenário A
    (escopo via `escopo(page)`). Compartilhado por Consumo/Permanente/Serviço.
    """
    logger.info("Iniciou seleção de conta contábil.")

    ctx = escopo(page)
    ctx.locator("button[name='lookup-complemento_CdConta']").click()
    aguardar_ajax_global(page)

    if ctx.locator("input[name='complemento_CdConta']").is_visible() and ctx.locator("input[name='complemento_CdConta']").input_value() != "":
        return True

    if ctx.locator(".alert-warning").count() > 0:
        logger.info(ctx.locator(".alert-warning").inner_text())
        return False

    linhas = (
        ctx.locator("table[name='paginationTable'] tbody tr")
        .filter(has_not_text="HOSPITALAR")
        .filter(has_not_text="¿")
        .filter(has_not_text="ODONTOLOGICO")
    )

    total = linhas.count()
    if total == 0:
        raise ValueError("Nenhuma conta contábil disponível.")

    linhas.nth(random.randrange(total)).locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de conta contábil.")

    return True
