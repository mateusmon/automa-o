from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_observacao(page: Page, material: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento da aba de observação para o material '{}'.", material['nome'])

    ctx = escopo(page)
    observacao = material["observacao"]

    ctx.get_by_role("button", name="Observações").click()
    aguardar_ajax_global(page)

    ctx.get_by_title("Adicionar observações").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo observação: '{}'.", observacao)
    ctx.locator("textarea[name='dsObs']").fill(observacao)

    ctx.get_by_role("button", name="Retornar").click()
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento da aba de observação para o material '{}'.", material['nome'])
