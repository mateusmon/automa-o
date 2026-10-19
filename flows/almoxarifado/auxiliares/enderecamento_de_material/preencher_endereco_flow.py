from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax, esperar_sucesso_ou_erro, preencher_campo


def preencher_endereco(page: Page) -> None:
    logger.info("Cadastrando endereçamento.")

    ctx = escopo(page)

    proxima_ordem = ctx.locator("table.tabela tbody[name='tboItens'] tr").count() + 1

    add_botao = ctx.locator("button[name='submitAddLine1']")
    add_botao.wait_for(state="visible")
    clicar_com_ajax(ctx, add_botao)

    campo_endereco = ctx.locator(f"input[name='endereco-{proxima_ordem}-3']")
    campo_endereco.wait_for(state="visible")
    logger.info("Preenchendo endereço 'endereçado'.")
    preencher_campo(ctx, campo_endereco, "endereçado")
    logger.info("Preenchendo UM 'UMT'.")
    preencher_campo(ctx, f"input[name='um-{proxima_ordem}-4']", "%")

    clicar_com_ajax(ctx, "button[name='submitFinish']")
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou o cadastro do endereçamento.")