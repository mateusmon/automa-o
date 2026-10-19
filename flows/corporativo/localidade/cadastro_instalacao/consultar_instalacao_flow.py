from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_instalacao(page: Page, instalacao: dict) -> None:
    """
    Abre a Consulta de Instalação e filtra por `model-2` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param instalacao: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de Instalação '{}'.", instalacao["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando Instalação pelo Nome: '{}'.", instalacao["nome"])
    ctx.locator("input[name='model-2']").fill(instalacao["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Instalação '{}'.", instalacao["nome"])
