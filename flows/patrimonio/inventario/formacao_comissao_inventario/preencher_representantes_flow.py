from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, esperar_sucesso_ou_erro
from utils.geradores import gerar_numero_com_digitos


def preencher_representantes(page: Page, funcionario: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos representantes.")

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='representantes-1-2']", funcionario["nome"])
    ctx.locator("input[name='cdFuncionarioSelecionado'][rowid='1']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo campo de Número do Processo com valor gerado aleatoriamente '{}'.", gerar_numero_com_digitos(10))
    ctx.locator("input[name='nrProcesso']").fill(gerar_numero_com_digitos(10))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou o preenchimento dos representantes.")
