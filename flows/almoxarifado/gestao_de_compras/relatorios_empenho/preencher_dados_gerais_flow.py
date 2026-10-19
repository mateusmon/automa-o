from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict) -> bool:
    logger.info("Preenchendo dados gerais de relatórios de empenho.")

    # Usuário com acesso a várias UGs: campo de busca a preencher.
    # Usuário com acesso a uma única UG: vem como <select name="listaUg"> já pré-selecionado.
    if not page.locator("select[name='listaUg']"):
        logger.info("Preenchendo UG '{}'.", ug_data["nome"])
        preencher_campo(page, "input[name='ugs']", ug_data["nome"])

    # Preenchendo as datas
    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")
    ano_atual = obter_data_almoxarifado(page, "YYYY/MM").split("/")[0]
    logger.info(
        "Preenchendo datas de inclusão de '{}' a '{}'.", "01/01/" + ano_atual, data_hoje
    )
    page.locator("input[name='dtInclusao1']").press_sequentially(
        "0101" + ano_atual, delay=50
    )
    page.locator("input[name='dtInclusao2']").press_sequentially(data_hoje, delay=50)
    page.locator("h1:has-text('Relatórios - Empenho')").click()

    logger.info("Preenchimento de dados gerais de relatórios de empenho.")

    return True
