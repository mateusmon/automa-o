from typing import Literal
from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, select_tipo


def preencher_dados_gerais(page: Page, tipo: Literal["INTERNA", "EXTERNA"]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais do motivo de saída temporária.")

    ctx = escopo(page)

    logger.info("Selecionando tipo do motivo de saída temporária: '{}'.", tipo)
    select_tipo(ctx, "inInterna", tipo)

    logger.info("Preenchendo motivo de saída temporária: 'MOTIVO PLAUSÍVEL DE SAÍDA'.")
    ctx.type("input[name='nmMotivoSaidaTemp']", "MOTIVO PLAUSÍVEL DE SAÍDA", delay=50)
    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Finalizou o preenchimento dos dados gerais do motivo de saída temporária.")
