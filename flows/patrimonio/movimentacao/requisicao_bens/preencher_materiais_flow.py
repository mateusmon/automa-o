from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import esperar_sucesso_ou_erro, preencher_campo


def preencher_materiais(page: Page, bem: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento de materiais. Bem: '{}'.", bem["nome"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='cdBemServico-1-3']", f"{bem['nome']} {bem['complemento']}")
    logger.info("Preenchido o campo de bem/serviço. Bem: '{}'.", bem["nome"])
    ctx.locator("input[name='qtRequisicao-2-4']").fill("1")

    ctx.click("button[name='submitFinish']")
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou o preenchimento de materiais. Bem: '{}'.", bem["nome"])
