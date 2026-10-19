from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def preencher_dados_gerais_completo(page: Page, almoxarifado: dict[str, str], ur: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados gerais no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    _preencher(ctx, almoxarifado, ur)

    logger.info("Finalizou preenchimento de dados gerais no almoxarifado '{}'.", almoxarifado["nome"])


def _preencher(ctx, almoxarifado: dict[str, str], ur: dict[str, str]) -> None:
    # 1. Abre a modal e realiza a busca filtrada
    clicar_com_ajax(ctx, ctx.locator("button[name='lookup-ur']"))
    logger.info("Preenchendo sigla da UR: '{}'.", ur["sigla_ua"])
    preencher_campo(ctx, "input[name='model-2']", ur["sigla_ua"])
    clicar_com_ajax(ctx, ctx.locator("button[name='submitSearch']"))

    # 2. Localiza a linha correta dentre as 4 opções e clica no botão de anexar
    nome_ur = ur["nome"]
    logger.info("Selecionando a UR '{}' na listagem de resultados...", nome_ur)

    linha_ur = ctx.locator("tbody tr", has_text=nome_ur)

    if linha_ur.count() > 0:
        btn_anexar = linha_ur.first.locator("button[name='submitUse'].btnAnexar")
        clicar_com_ajax(ctx, btn_anexar)
        logger.info("UR '{}' selecionada com sucesso.", nome_ur)
    else:
        raise RuntimeError(
            f"A UR '{nome_ur}' não foi encontrada entre as opções retornadas pela busca."
        )

    # 3. Dá sequência ao preenchimento dos campos restantes
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
