from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, clicar_com_ajax


def consultar_subgrupo_supply(page: Page, supply: dict) -> None:
    """
    Carrega o subgrupo do registro Supply para exclusão. Cenário A. Abre o lookup, muda o
    nível do filtro para SUBGRUPO, filtra pelo código do subgrupo e dá duplo clique no nó
    do subgrupo na árvore (que carrega o registro e habilita o Excluir).

    :param supply: dict do blueprint (usa a chave `subgrupo_codigo`).
    """
    logger.info("Iniciou consulta de subgrupo do Supply.")

    ctx = escopo(page)

    btn_lookup = ctx.locator("button[name='lookup-grupoDsExemplo']")
    clicar_com_ajax(ctx, btn_lookup)

    ctx.locator("select[name='tpFil']").select_option(label="SUBGRUPO")
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='filtro']", supply["subgrupo_codigo"])
    ctx.locator("img.x-tree-node-icon.icon-subgrupo-open").dblclick()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de subgrupo do Supply.")
