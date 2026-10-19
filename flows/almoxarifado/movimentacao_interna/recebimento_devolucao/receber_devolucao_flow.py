from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def efetuar_recebimento_devolucao(page: Page, almoxarifado: dict[str, str]) -> None:
    logger.info("Iniciou recebimento da devolução de materiais no almoxarifado: {}.", almoxarifado["nome"])

    ctx = escopo(page)
    nome = almoxarifado["nome"]

    linha = ctx.locator("table.tabela tbody tr").filter(has=ctx.locator("td").nth(3).filter(has_text=nome)).first

    logger.info("Selecionando devolução de materiais para o almoxarifado: {}.", nome)
    linha.locator("input[type='checkbox']").check()
    logger.info("Clicando no botão de finalizar recebimento da devolução de materiais.")
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou recebimento da devolução de materiais no almoxarifado: {}.", almoxarifado["nome"])
