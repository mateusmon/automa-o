from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def autorizar_pedido(page: Page) -> bool:
    logger.info("Iniciou autorização de pedido.")

    ctx = escopo(page)

    tabela = ctx.locator("table.tabelaComRolagem")
    tabela.wait_for(state="visible")

    linhas_tabela = tabela.locator("tbody[name='pedidosTBody'] tr")
    count = linhas_tabela.count()

    if not count:
        logger.info("Não há pedidos disponíveis para fazer autorização.")
        return False
    
    linha = linhas_tabela.last

    linha.locator('select[name^="pedido-cmbAutorizar"]').select_option("AUTORIZAR")

    logger.info("Finalizou autorização de pedido.")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    return True
