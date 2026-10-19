from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def escolher_classificacao(page: Page, classificacao: str) -> None:
    logger.info("Iniciou escolha de classificação '{}'.", classificacao)

    mapa = {
        "NATUREZA": "modoNatureza",
        "CONSUMO": "modoConsumo",
        "CRITICIDADE": "modoCriticidade",
        "VALOR": "modoValor"
    }

    ctx = escopo(page)
    ctx.locator(f"input[name='{mapa[classificacao]}']").check()
    aguardar_ajax_global(page)

    logger.info("Finalizou escolha de classificação '{}'.", classificacao)
