from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    esperar_sucesso_ou_erro,
    select_tipo,
)


def alterar_baixa_bens(page: Page) -> bool:
    logger.info("Alterando baixa de bens.")

    ctx = escopo(page)

    data = obter_data_patrimonio(ctx, "DDMMYYYY")

    campo_situacao = ctx.locator("select[name='situacaoBaixa']")

    if campo_situacao.is_disabled():
        logger.warning("O campo utilizado para a alteração está desabilitado.")
        return False

    if campo_situacao.locator("option:checked").inner_text() == "AUTORIZADA":
        select_tipo(ctx, "situacaoBaixa", "EM ANDAMENTO")
    else:
        select_tipo(ctx, "situacaoBaixa", "AUTORIZADA")
        ctx.locator("input[name='dtContabil']").press_sequentially(data, delay=50)

    aguardar_ajax_global(page)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitFinish']"))

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Baixa de bens alterado.")
    return True
