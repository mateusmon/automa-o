from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais(page: Page) -> None:
    logger.info("Iniciou preenchimento de dados do Roteiro Padrão para Baixa.")

    ctx = escopo(page)

    logger.info("Preenchendo nome do Roteiro Padrão para Baixa: 'ROTEIRO DE BAIXA'.")
    ctx.fill("input[name='dsRoteiro']", "ROTEIRO DE BAIXA")
    logger.info("Preenchendo primeira forma de operação do Roteiro Padrão para Baixa.")
    preencher_campo(ctx, "input[name='formaOperacao']", "   ")
    logger.info("Preenchendo tarefa do Roteiro Padrão para Baixa: 'TAREFA AUTOMATIZADA'.")
    ctx.fill("input[name='tarefas-1-3']", "TAREFA AUTOMATIZADA")

    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados do Roteiro Padrão para Baixa.")
