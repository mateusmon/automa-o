from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_material(page: Page, material: dict) -> bool:
    logger.info("Iniciou seleção de material '{}'.", material["nome"])

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    ctx = escopo(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has_text=nome_completo_material
    ).first

    try:
        expect(linha).to_be_visible(timeout=3_000)
    except AssertionError:
        logger.info("Nenhum material encontrado para '{}'.", nome_completo_material)
        return False

    linha.locator("input[type='checkbox']").check()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de material.")
    return True
