from playwright.sync_api import Page, expect
from loguru import logger

from utils.waits import preencher_autocomplete


def preencher_almoxarifado_fornecedor(page: Page, almoxarifado: dict, fornecedor: dict):
    logger.info("Inicou preenchimento do almoxarifado '{}' e fornecedor '{}'.", almoxarifado["nome"], fornecedor["nome"])

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_autocomplete(page, "#almoxarifado", almoxarifado["sigla"])
    # Espere até os demais campos serem preenchidos automaticamente
    expect(page.locator('input[name="ug"]')).not_to_have_value("")
    # Fornecedor
    logger.info("Preenchendo nome do fornecedor: '{}'.", fornecedor["nome"])
    preencher_autocomplete(page, "#agenteEntrada", fornecedor["nome"])

    logger.info("Almoxarifado '{}' e fornecedor '{}' preenchidos com sucesso.", almoxarifado["nome"], fornecedor["nome"])
