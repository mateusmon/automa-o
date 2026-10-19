from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais_completo(page: Page, ul: dict[str, str], modalidade: str = "PERMANENTE", patrimonio_antigo: str = "SEM") -> None:
    logger.info("Iniciou o preenchimento dos dados gerais completo.")

    endereco = ul["endereco"]

    data = obter_data_patrimonio(page)

    ctx = escopo(page)

    if modalidade == "PERMANENTE":
        ctx.locator("input[name='exigeAssinatura'][value='false']").check()
        aguardar_ajax_global(page)
    else:
        ctx.locator("input[name='exigeAssinatura'][value='true']").check()
        aguardar_ajax_global(page)

        select = ctx.locator("select[name='motivoSaidaTemp']")
        select.wait_for(state="visible")

        for opcao in select.locator("option").all():
            valor = opcao.get_attribute("value")

            select.select_option(valor)
            aguardar_ajax_global(page)

            expect(select).to_have_value(valor)

        data_retorno = ctx.locator("input[name='dtPrevRetorno']")
        data_retorno.wait_for(state="visible")
        if data_retorno.is_enabled():
            data_retorno.fill(data)

    if patrimonio_antigo == "SEM":
        ctx.locator("input[name='opcaoPatrAnt'][value='N']").check()
        aguardar_ajax_global(page)
    else:
        ctx.locator("input[name='opcaoPatrAnt'][value='S']").check()
        aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='ulDestino']", endereco)

    data_trans = ctx.locator("input[name='dtTransferencia']")
    if data_trans.is_visible() and data_trans.is_enabled():
        data_trans.fill(data)

    logger.info("Finalizou o preenchimento dos dados gerais completo.")
