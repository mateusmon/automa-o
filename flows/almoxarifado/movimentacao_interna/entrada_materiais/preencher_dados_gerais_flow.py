from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict[str, str], fornecedor: dict[str, str], orgao_externo: dict[str, str] | None = None) -> None:
    logger.info("Preenchendo dados gerais no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)

    # Almoxarifado
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    campo_almoxarifado = ctx.locator("input[name='almoxarifado']")
    campo_almoxarifado.wait_for(state="visible")
    preencher_campo(ctx, campo_almoxarifado, almoxarifado["sigla"])

    # Espere até os demais campos serem preenchidos automaticamente
    expect(ctx.locator('input[name="ug"]')).not_to_have_value("")

    # Datas
    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")

    data_recebimento = ctx.locator('input[name="dtRecebimento"]')
    data_atesto = ctx.locator('input[name="dtContabil"]')

    logger.info("Preenchendo data de recebimento: '{}'.", data_hoje)
    data_recebimento.clear()
    data_recebimento.type(data_hoje, delay=50)

    if data_atesto.is_enabled():
        logger.info("Preenchendo data de atesto: '{}'.", data_hoje)
        data_atesto.clear()
        data_atesto.type(data_hoje, delay=50)

    # Foi necessário fazer dessa forma, pois, dependendo do tipo de entrada,
    # o campo Agente de Entrada pode ser "Fornecedor", "Órgão Externo" ou "UR".
    clicar_com_ajax(ctx, "button[name='lookup-agenteEntrada']")

    campo_fornecedor = ctx.locator("tbody[name='searchFieldsData'] tr td").filter(has_text="Fornecedor").first.count()
    campo_orgao_externo = ctx.locator("tbody[name='searchFieldsData'] tr td").filter(has_text="Orgão Externo").first.count()

    clicar_com_ajax(ctx, "button[name='submitCancel']")

    # Fornecedor
    if campo_fornecedor > 0:
        logger.info("Preenchendo fornecedor '{}'.", fornecedor["nome"])
        preencher_campo(ctx, "#agenteEntrada", fornecedor["nome"])

    elif campo_orgao_externo > 0:
        logger.info("Preenchendo órgão externo '{}'.", orgao_externo["nome"])
        preencher_campo(ctx, "#agenteEntrada", orgao_externo["nome"])

    else:
        logger.info("Não é fornecedor nem Órgão Externo")
        preencher_campo(ctx, "#agenteEntrada", "%")

    logger.info("Dados gerais no almoxarifado '{}' preenchidos com sucesso.", almoxarifado["nome"])
