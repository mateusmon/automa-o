from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_itens(page: Page, material_data: dict) -> None:
    logger.info("Preenchendo dados do material '{}' para o cadastro de previsão de consumo.", material_data["nome"])

    nome_completo = f"{material_data['nome']} {material_data['complemento']}"
    
    ctx = escopo(page)

    logger.info("Preenchendo material '{}'.", nome_completo)
    preencher_campo(ctx, "input[name='material-1-3']", nome_completo)

    ctx.locator("input[name='qtPrevRequisicao-2-7']").wait_for(state="visible")

    if ctx.locator("input[name='qtPrevRequisicao-2-7']").is_visible():
        logger.info("Preenchendo quantidade de previsão de consumo '1'.")
        ctx.locator("input[name='qtPrevRequisicao-2-7']").fill("1")
    
    else:
        logger.info("Preenchendo quantidade de previsão de consumo '1'.")
        ctx.locator("input[name='qtPrevRequisicao-1-7']").fill("1")

    logger.info("Preenchimento de dados do material '{}' para o cadastro de previsão de consumo finalizado.", material_data["nome"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
