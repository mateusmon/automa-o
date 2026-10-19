from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo
from flows.patrimonio.modificacao.alteracao_individual_bem.consultar_bem_flow import consultar_bem


def consultar_alteracao_individual_bem(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou consulta de alteração individual de bem.")

    ctx = escopo(page)
    nome_completo_bem = f"{bem['nome']} {bem['complemento']}"

    preencher_campo(ctx, "input[name='ugUl']", ug["codigo"])

    ctx.locator("button[name='lookup-bem']").click()
    aguardar_ajax_global(page)

    existe_bem = consultar_bem(page, ug, bem)
    aguardar_ajax_global(page)

    if not existe_bem:
        logger.info("Nenhum bem encontrado para o material '{}'.", nome_completo_bem)
        return False

    logger.info("Finalizou consulta de alteração individual de bem.")
    return True
