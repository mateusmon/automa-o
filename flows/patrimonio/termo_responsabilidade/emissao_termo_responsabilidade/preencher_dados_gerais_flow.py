from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax, esperar_sucesso_ou_erro, preencher_campo

def preencher_dados_gerais(page: Page, ug: dict[str, str], ua: dict[str, str]):
    logger.info("Iniciou o preenchimento dos dados gerais {}/{}.".format(ug["codigo"], ua["sigla"]))
    ctx = escopo(page)

    # Preenche U.G.
    preencher_campo(ctx, "input[name='cdUg']", ug["codigo"])

    # Preenche U.A
    preencher_campo(ctx, "input[name='cdUa']", ua["sigla"])

    # Assinatura eletrônica
    ctx.locator("input[name='inAssinatura'][value='S']").click()

    clicar_com_ajax(ctx, "button[name='submitFinish']")

    esperar_sucesso_ou_erro(ctx)

    logger.info("Dados gerais preenchidos {}/{}.".format(ug["codigo"], ua["sigla"]))
