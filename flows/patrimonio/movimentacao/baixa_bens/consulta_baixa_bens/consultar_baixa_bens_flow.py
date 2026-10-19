from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_baixa_bens(page: Page, ug: dict):
    logger.info("Consultando baixa de bens para a unidade gestora '{}'.", ug["nome"])
    ctx = escopo(page)

    data = obter_data_patrimonio(ctx, "DDMMYYYY")

    ctx.locator("button[name='submitSearch']").click()

    # Preencher unidade gestora
    preencher_campo(ctx, "input[name='model-2']", ug["codigo"], igual="True")

    logger.info("Filtrando baixa de bens pela unidade gestora '{}'.", ug["nome"])
    ctx.locator("input[name='model-9-from']").press_sequentially(data, delay=50)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Aguardar a tabela de paginação carregar.
    # Espera a tabela, não o tbody: com 0 resultados o tbody fica vazio e oculto.
    ctx.locator("table[name='paginationTable']").wait_for(state="visible")

    # Seleciona a última linha que corresponde à unidade gestora.
    # A aplicação insere a nova baixa na última posição da tabela.
    # Usar .last garante que interagimos com o registro recém‑criado.
    linha = (
        ctx.locator("table[name='paginationTable'] tbody tr")
        .filter(has=ctx.locator("td").nth(0).filter(has_text=ug["nome"]))
        .first
    )

    if linha.count() == 0:
        logger.info("Nenhuma baixa encontrada para a unidade gestora '{}'.", ug["nome"])
        return False

    linha.locator("button[name='submitUse']").click()

    aguardar_ajax_global(page)

    logger.info("Baixa de bens consultado para a unidade gestora '{}'.", ug["nome"])

    return True
