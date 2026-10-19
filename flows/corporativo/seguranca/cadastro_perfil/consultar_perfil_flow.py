from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_perfil(page: Page, perfil: dict) -> None:
    """
    Abre a Consulta de Perfil e filtra pelo Nome (`model-2`). Cenário A. Apenas filtra e
    dispara a busca — a seleção fica no flow seguinte.

    Filtros confirmados ao vivo: model-0 Sistema (lookup), model-1 Código (faixa),
    **model-2 Nome**, model-3 Usuário (lookup), model-4 Data de Bloqueio, model-5 Módulo,
    model-6..9 Restrições.

    :param perfil: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de Perfil '{}'.", perfil["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando Perfil pelo campo de Nome: '{}'.", perfil["nome"])
    ctx.locator("input[name='model-2']").fill(perfil["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Perfil '{}'.", perfil["nome"])
