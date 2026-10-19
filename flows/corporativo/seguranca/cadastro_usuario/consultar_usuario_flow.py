from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_usuario(page: Page, usuario: dict) -> bool:
    """
    Abre a Consulta de Usuário e filtra pelo Funcionário (`model-1`, lookup). Cenário A.
    Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    A consulta de Usuário é especial: `model-1` é um lookup que resolve o funcionário pelo
    nome (preenche + clica `lookup-model-1`). Se o funcionário não existir, aparece um aviso
    (`divWarningMsg`) e não há o que buscar — o flow retorna sem disparar a busca, e o
    `selecionar_usuario` seguinte trata como "não encontrado". Confirmado no Genesis
    (`usuario_service.py`).

    :param usuario: dict do blueprint (usa a chave `nome`, do funcionário).
    """
    logger.info("Iniciou consulta de Usuário '{}'.", usuario["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()  # abre a consulta
    aguardar_ajax_global(page)
    logger.info("Filtrando Usuário pelo campo de Funcionário: '{}'.", usuario["nome"])
    ctx.locator("input[name='model-1']").fill(usuario["nome"])
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    if ctx.locator("div[name='divWarningMsg']").is_visible():
        logger.info("Funcionário '{}' não encontrado no lookup da consulta.", usuario["nome"])
        return False

    ctx.locator("button[name='submitSearch']").click()  # dispara a busca
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Usuário '{}'.", usuario["nome"])
    return True