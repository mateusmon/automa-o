from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def efetuar_recebimento_transferencia(page: Page, almoxarifado: dict) -> bool:
    logger.info("Iniciou recebimento de transferência entre almoxarifados.")

    ctx = escopo(page)

    nome_almoxarifado = almoxarifado["nome"]

    ctx.locator("button[name='submitFinish']").wait_for(state="visible")
    ctx.locator("button[name='submitTabSearchData']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo almoxarifado: '{}'.", nome_almoxarifado)
    preencher_campo(ctx, "input[name='model-1']", nome_almoxarifado)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = (
        ctx.locator("table[name='paginationTable'] tbody tr")
        .filter(has=ctx.locator("td").filter(has_text=nome_almoxarifado))
        .filter(has_text="ATENDIDA")
        .first
    )

    ctx.locator("button[name='submitFinish']").wait_for(state="visible")

    if linha.count() == 0:
        logger.info(
            "Nenhuma transferência com recebimento pendente encontrada para o almoxarifado '{}'.",
            nome_almoxarifado,
        )
        return False

    logger.info(
        "Selecionando recebimento de transferência para o almoxarifado '{}'.",
        nome_almoxarifado,
    )
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    if ctx.locator("input[name='dtFinalizada']").is_enabled():
        data_almox = obter_data_almoxarifado(page, "DDMMYYYY")
        ctx.locator("input[name='dtFinalizada']").clear()
        ctx.locator("input[name='dtFinalizada']").press_sequentially(
            data_almox, delay=50
        )
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.success("Finalizou recebimento de transferência entre almoxarifados.")
    return True
