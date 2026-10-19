from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, preencher_autocomplete_select


def preencher_natureza_estoque(page: Page, material: dict, natureza: str) -> None:
    nome_completo = f"{material['nome']} {material['complemento']}"

    logger.info("Iniciou preenchimento de natureza de estoque.")

    ctx = escopo(page)

    logger.info("Preenchendo natureza de estoque '{}'.", natureza)
    preencher_autocomplete_select(ctx, "input[name='tpUsoEstoque']", natureza)
    logger.info("Preenchendo nome do material '{}'.", nome_completo)
    preencher_campo(ctx, "input[name='bemServico']", nome_completo)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de natureza de estoque.")
