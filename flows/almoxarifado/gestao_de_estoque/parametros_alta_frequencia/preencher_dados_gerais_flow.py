from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict, es: str = "60", lc: str = "360", em: str = "240") -> None:
    logger.info("Iniciou preenchimento de dados gerais da política de compras de alta frequência.")

    valorA = "70"
    valorB = "20"
    valorC_NC = "5"

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdAlmoxarifado']", almoxarifado["sigla"])

    logger.info("Preenchendo 'valor A' da política de compras de alta frequência.")
    input_valorA = ctx.locator("input[name='pcValor-1-2']")
    input_valorA.dblclick()
    input_valorA.type(valorA, delay=50)

    logger.info("Preenchendo 'valor B' da política de compras de alta frequência.")
    input_valorB = ctx.locator("input[name='pcValor-2-2']")
    input_valorB.dblclick()
    input_valorB.type(valorB, delay=50)

    logger.info("Preenchendo 'valor C' da política de compras de alta frequência.")
    input_valorC = ctx.locator("input[name='pcValor-3-2']")
    input_valorC.dblclick()
    input_valorC.type(valorC_NC, delay=50)

    logger.info("Preenchendo 'valor NC' da política de compras de alta frequência.")
    input_valorNC = ctx.locator("input[name='pcValor-4-2']")
    input_valorNC.dblclick()
    input_valorNC.type(valorC_NC, delay=50)

    linhas = ctx.locator("table.tabela tbody tr")
    total_linhas = linhas.count()

    for i in range(total_linhas):
        linha = linhas.nth(i)

        logger.info("Preenchendo 'es' da política de compras de alta frequência na linha {}.", i + 1)
        input_es = linha.locator("td").nth(2).locator("input[type='text']")
        input_es.dblclick()
        input_es.type(es, delay=50)

        logger.info("Preenchendo 'lc' da política de compras de alta frequência na linha {}.", i + 1)
        input_lc = linha.locator("td").nth(3).locator("input[type='text']")
        input_lc.dblclick()
        input_lc.type(lc, delay=50)

        logger.info("Preenchendo 'em' da política de compras de alta frequência na linha {}.", i + 1)
        input_em = linha.locator("td").nth(4).locator("input[type='text']")
        input_em.dblclick()
        input_em.type(em, delay=50)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais da política de compras de alta frequência.")
