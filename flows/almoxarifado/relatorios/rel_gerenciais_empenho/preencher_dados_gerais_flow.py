from datetime import datetime

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str]):
    logger.info(
        "Iniciou preenchimento de dados gerais de relatórios de empenho na UG '{}'.",
        ug_data["nome"],
    )

    ctx = escopo(page)
    campo_ug = ctx.locator("select[name='listaUg'], input[name='ugs']").first
    tag_name = campo_ug.evaluate("el => el.tagName.toLowerCase()")

    if tag_name == "input":
        logger.info("Preenchendo nome da UG: '{}'.", ug_data["nome"])
        preencher_campo(
            ctx, "input[name='ugs']", ug_data["nome"], lookup_name="lookup-ug"
        )

    data_hoje = datetime.today().strftime("%d%m%Y")
    ano_atual = datetime.today().strftime("%Y")
    logger.info("Preenchendo data de inclusão inicial: '01/01/{}'.", ano_atual)
    ctx.locator("input[name='dtInclusao1']").type("0101" + ano_atual)
    logger.info("Preenchendo data de inclusão final: '{}'.", data_hoje)
    ctx.locator("input[name='dtInclusao2']").type(data_hoje)

    logger.info(
        "Finalizou preenchimento de dados gerais de relatórios de empenho na UG '{}'.",
        ug_data["nome"],
    )
