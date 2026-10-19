from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def preencher_dados_gerais_sem_autocomplete(page: Page, almoxarifado: dict[str, str], fornecedor: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento do Almoxarifado '{}' e do Fornecedor '{}'.", almoxarifado["nome"], fornecedor["nome"])

    ctx = escopo(page)

    # 1. Seleção do Almoxarifado via Consulta Avançada
    logger.info("Selecionando Almoxarifado via Consulta Avançada.")
    clicar_com_ajax(ctx, "button[name='lookup-almoxarifado']")
    
    # Aguarda a abertura da modal/campo de consulta
    expect(ctx.locator("#model-4")).to_be_visible()
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    ctx.locator("#model-4").fill(almoxarifado["sigla"])
    if "nome" in almoxarifado:
        logger.info("Preenchendo nome do almoxarifado: '{}'.", almoxarifado["nome"])
        ctx.locator("#model-3").fill(almoxarifado["nome"])
        
    clicar_com_ajax(ctx, "button[title='Consultar novo registro']")
    
    # Aguarda o botão Anexar ficar pronto e clica
    btn_anexar_almox = ctx.locator("button[name='submitUse'], button[title='Anexar']")
    expect(btn_anexar_almox.first).to_be_visible()
    clicar_com_ajax(ctx, "button[name='submitUse'], button[title='Anexar']")

    # Garante que a modal fechou e os campos vinculados (ex: UG) foram atualizados
    expect(ctx.locator("input[name='ug']")).not_to_have_value("")
    logger.info("Selecionando Fornecedor via Autocomplete.")

    logger.info("Preenchendo nome do fornecedor: '{}'.", fornecedor["nome"])
    preencher_campo(ctx, 'input[name="agenteEntrada"]', fornecedor["nome"])

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

    logger.info("Finalizou o preenchimento do Almoxarifado '{}' e do Fornecedor '{}'.", almoxarifado["nome"], fornecedor["nome"])
