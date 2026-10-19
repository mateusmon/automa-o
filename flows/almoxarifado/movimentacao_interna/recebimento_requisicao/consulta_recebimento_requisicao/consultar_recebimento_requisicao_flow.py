from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_recebimento_requisicao(
    page: Page,
    ur: dict[str, str],
    almoxarifado: dict[str, str],
    material: dict[str, str],
) -> None:
    logger.info(
        "Iniciou consulta de recebimento de requisição no almoxarifado '{}'.",
        almoxarifado["nome"],
    )

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.locator("button[name='submitTabConsulta']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(
        ctx, ctx.locator("input[name='almoxarifado']"), almoxarifado["sigla"]
    )
    # Não existe sigla na ur. Apenas a sigla da UA
    logger.info("Preenchendo da UR: '{}'.", ur["nome"])
    preencher_campo(ctx, ctx.locator("input[name='ur']"), ur["nome"])
    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(
        ctx, ctx.locator("input[name='bemServico']"), nome_completo_material
    )
    logger.info("Preenchendo situação da requisição: 'FINALIZADA'.")
    preencher_campo(
        ctx,
        ctx.locator("input[name='situacaoRequisicao']"),
        "FINALIZADA",
        lookup_name="lookup-situacaRequisicao",
    )

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info(
        "Finalizou consulta de recebimento de requisição no almoxarifado '{}'.",
        almoxarifado["nome"],
    )
