from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_almoxarifado_solicitante(
    page: Page,
    almoxarifado: dict[str, str],
    material: dict[str, str],
    quantidade: str = "1",
) -> None:
    logger.info("Iniciou preenchimento de almoxarifado solicitante '{}'.", almoxarifado["nome"])

    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx = escopo(page)
    _preencher_campos(ctx, page, almoxarifado, nome_completo_material, quantidade)

    logger.info("Finalizou preenchimento de almoxarifado solicitante.")


def _preencher_campos(ctx, page: Page, almoxarifado: dict[str, str], nome_completo_material: str, quantidade: str) -> None:
    logger.info("Preenchendo sigla do almoxarifado solicitante: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifadoDestino']", almoxarifado["sigla"])

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='cdBemServico-1-3']", nome_completo_material)

    logger.info("Preenchendo quantidade de transferência: '{}'.", quantidade)
    field_quantidade = ctx.locator("input[name='qtRequisicao-2-5']")
    field_quantidade.click()
    field_quantidade.fill(quantidade)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
