from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def selecionar_requisicao(page: Page, ul: dict[str, str]) -> bool:
    logger.info("Iniciou a seleção de requisição para atendimento da UL '{}'.", ul["sigla"])

    sigla = ul["sigla"]

    ha_requisicoes = _selecionar(page, sigla)

    if not ha_requisicoes:
        logger.info("Nenhuma requisição encontrada para '{}'.", sigla)
        return ha_requisicoes
    
    logger.info("Finalizou a seleção de requisição para atendimento da UL '{}'.", ul["sigla"])
    return ha_requisicoes


def _selecionar(page: Page, sigla: str) -> bool:
    ctx = escopo(page)

    linha = ctx.locator("table.tabela tbody[name='tabRec'] tr").filter(
        has=ctx.locator("td").nth(4).filter(
            has_text=sigla
        )
    )

    if linha.count() == 0:
        return False

    linha.last.locator("button[name='submitUse']").click()

    return True
