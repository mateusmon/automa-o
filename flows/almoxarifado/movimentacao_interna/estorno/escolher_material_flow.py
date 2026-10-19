from decimal import Decimal

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def escolher_material(page: Page, material: dict) -> None:
    logger.info("Iniciou escolha do material: {}.", material["nome"])

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"
    preco_unitario = material["preco_unitario"].replace(",", ".")
    valor = str(Decimal(preco_unitario) * 2).replace(".", ",")

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='novoBemServico-1-2']", nome_completo_material)

    logger.info("Preenchendo quantidade: '2'.")
    ctx.locator("input[name='qtAtual-1-6']").fill("2")
    logger.info("Preenchendo valor: '{}'.", valor)
    ctx.locator("input[name='vlAtual-1-7']").fill(valor)

    if ctx.locator("input[name='dtContabil']").is_enabled():
        ctx.locator("input[name='dtContabil']").clear()
        ctx.locator("input[name='dtContabil']").press_sequentially(
            obter_data_almoxarifado(page, "DDMMYYYY"), delay=5
        )

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou escolha do material: {}.", material["nome"])
