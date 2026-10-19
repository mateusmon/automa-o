from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_modificacao_material(page: Page, bem: dict[str, str], bem_novo: dict[str, str]) -> None:
    logger.info("Iniciou consulta de modificação de material {}.", bem["nome"])

    ctx = escopo(page)
    nome_completo_bem = f"{bem['nome']} {bem['complemento']}"
    nome_completo_bem_novo = f"{bem_novo['nome']} {bem_novo['complemento']}"

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-2']", nome_completo_bem)
    preencher_campo(ctx, "input[name='model-3']", nome_completo_bem_novo)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de modificação de material {}.", bem["nome"])
