from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_materiais(page: Page, bem: dict[str, str], quantidade="1") -> None:
    nome_bem = bem["nome"]
    complemento_bem = bem["complemento"]
    nome_completo_bem = f"{nome_bem} {complemento_bem}"
    preco_unitario = bem["preco_unitario"]

    logger.info("Iniciou preenchimento de materiais para o bem '{}'.", nome_completo_bem)

    ctx = escopo(page)

    ctx.get_by_role("button", name="Materiais").click()

    aguardar_ajax_global(page)

    preencher_campo(ctx, 'input[name="bemServOrgao-1-3"]', nome_completo_bem)

    quantidade_input = ctx.locator('input[name="quantidade-1-4"]')
    # .clear() não funciona aqui, por algum motivo. Usei .select_text() no lugar
    quantidade_input.select_text()
    quantidade_input.type(quantidade, delay=50)

    valor_input = ctx.locator('input[name="valor-1-6"]')
    valor_input.clear()
    valor_input.type(preco_unitario, delay=50)

    valor_total_input = ctx.locator('input[name="vlTotalNF"]')
    valor_total_input.clear()
    valor_total_input.type(preco_unitario, delay=50)

    logger.info("Finalizou preenchimento de materiais para o bem '{}'.", nome_completo_bem)
