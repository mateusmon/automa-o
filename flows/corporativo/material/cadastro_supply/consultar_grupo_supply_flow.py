from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_grupo_supply(page: Page, supply: dict) -> None:
    """
    Carrega o grupo do registro Supply para exclusão. Cenário A. Só é possível excluir o
    grupo depois que o subgrupo já foi removido (grupo vazio). Abre o lookup, filtra pelo
    código do grupo (nível GRUPO) e dá duplo clique no nó do grupo na árvore.

    :param supply: dict do blueprint (usa `grupo_codigo` e `grupo_nome`).
    """
    logger.info("Iniciou consulta de grupo do Supply.")

    ctx = escopo(page)

    ctx.locator("button[name='lookup-grupoDsExemplo']").click()
    aguardar_ajax_global(page)

    ctx.locator("select[name='tpFil']").select_option(label="GRUPO")
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='filtro']", supply["grupo_codigo"])
    ctx.get_by_text(f"{supply['grupo_codigo']} - {supply['grupo_nome']}").first.dblclick()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de grupo do Supply.")
