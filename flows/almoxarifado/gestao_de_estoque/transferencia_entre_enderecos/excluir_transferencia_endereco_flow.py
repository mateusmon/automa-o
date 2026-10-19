from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def excluir_transferencia_endereco(page: Page, almoxarifado: dict[str, str], material: dict[str, str]) -> None:
    logger.info("Iniciou exclusão de transferência entre endereços no almoxarifado '{}'.", almoxarifado["nome"])

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado["sigla"])
    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='model-4']", nome_completo_material)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").filter(has_text=almoxarifado["nome"])
    ).first

    if linha.count() == 0:
        logger.info("Nenhuma transferência encontrada para o almoxarifado '{}'.", almoxarifado["nome"])
        return

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    page.once("dialog", lambda dialog: dialog.accept())
    ctx.locator("button[name='submitDelete']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou exclusão de transferência entre endereços no almoxarifado '{}'.", almoxarifado["nome"])
