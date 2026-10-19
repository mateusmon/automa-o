from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict, material: dict) -> None:
    logger.info("Preenchendo dados gerais.")
    
    sigla_almoxarifado = almoxarifado["sigla"]
    nome_material = material["nome"]

    ctx = escopo(page)

    logger.info("Preenchendo almoxarifado '{}'.", sigla_almoxarifado)
    preencher_campo(ctx, "input[name='almoxarifado']", sigla_almoxarifado)
    logger.info("Preenchendo material '{}'.", nome_material)
    preencher_campo(ctx, "input[name='material']", nome_material)

    logger.info("Preenchimento de dados gerais finalizado.")
