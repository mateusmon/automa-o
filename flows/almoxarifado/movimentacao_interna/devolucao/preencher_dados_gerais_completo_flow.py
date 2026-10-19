from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def preencher_dados_gerais_completo(
    page: Page, almoxarifado: dict[str, str], ur: dict[str, str]
) -> None:
    logger.info("Iniciou preenchimento de dados gerais da devolução.")

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
    expect(ctx.locator('input[name="ug"]')).not_to_have_value("")

    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")
    campo_data = ctx.locator('input[name="dtRecebimento"]')
    if campo_data.is_enabled():
        campo_data.clear()
        campo_data.type(data_hoje, delay=50)

    # 1. Abre a modal e realiza a busca filtrada
    clicar_com_ajax(ctx, ctx.locator("button[name='lookup-agenteEntrada']"))
    preencher_campo(ctx, "input[name='model-2']", ur["sigla_ua"])
    clicar_com_ajax(ctx, ctx.locator("button[name='submitSearch']"))

    # 2. Localiza a linha correta dentre as 4 opções e clica no botão de anexar
    nome_ur = ur["nome"]
    logger.info(f"Selecionando a UR '{nome_ur}' na listagem de resultados...")

    linha_ur = ctx.locator("tbody tr", has_text=nome_ur)

    if linha_ur.count() > 0:
        btn_anexar = linha_ur.first.locator("button[name='submitUse'].btnAnexar")
        clicar_com_ajax(ctx, btn_anexar)
        logger.info(f"UR '{nome_ur}' selecionada com sucesso.")
    else:
        raise RuntimeError(
            f"A UR '{nome_ur}' não foi encontrada entre as opções retornadas pela busca."
        )

    logger.info("Finalizou preenchimento de dados gerais da devolução.")
