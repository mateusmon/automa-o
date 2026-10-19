from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def excluir_dias_requisicao(page: Page, ur: dict) -> None:
    ur_nome = ur["nome"]

    ctx = escopo(page)

    logger.info("Excluindo os dias de requisição cadastrados no calendário da UR '{}'.", ur_nome)

    preencher_campo(ctx, "input[name='ur']", ur_nome)

    linha_calendario = ctx.locator("table.tabela tbody tr").filter(
        has=ctx.locator("td").nth(0)
    ).first

    linha_calendario.locator("input[type='checkbox']").check()
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
