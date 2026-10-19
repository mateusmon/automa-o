from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, select_tipo


def selecionar_tipo_autorizacao(page: Page, tipo: str) -> bool:
    logger.info("Iniciou autorização de pedido.")

    ctx = escopo(page)

    tabela = ctx.locator("table.tabelaComRolagem")
    tabela.wait_for(state="visible")

    linhas_tabela = tabela.locator("tbody[name='pedidosTBody'] tr")
    count = linhas_tabela.count()

    if not count:
        logger.info("Não há pedidos disponíveis para fazer autorização.")
        return False

    logger.info("Selecionando tipo de autorização '{}'.", tipo)
    select_tipo(ctx, "pedido-cmbAutorizar-1-1", tipo)
    logger.info("Preenchendo motivo da autorização.")
    ctx.locator("input[name='pedido-txMotivo-1-2']").type("MOTIVO PLAUSÍVEL", delay=50)

    logger.info("Finalizou autorização de pedido.")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    return True
