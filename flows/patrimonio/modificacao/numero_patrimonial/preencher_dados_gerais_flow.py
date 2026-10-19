from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo
from flows.patrimonio.shared.consultar_bem_flow import consultar_bem


def preencher_dados_gerais(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de dados gerais de número patrimonial {}.", bem["nome"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ug']", ug["codigo"])

    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)

    existe_bem = consultar_bem(page, ug, bem)

    if not existe_bem:
        logger.info("Nenhum bem com nome '{}' encontrado para seleção.", bem["nome"])
        return False

    ultima_linha = ctx.locator("table.tabelaComRolagem tbody tr").last
    ultima_linha.locator("td button[title='Gera o último número disponível']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de número patrimonial {}.", bem["nome"])
    return True
