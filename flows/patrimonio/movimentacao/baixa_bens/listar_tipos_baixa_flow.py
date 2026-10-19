from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def listar_tipos_baixa(page: Page) -> list[str]:
    logger.info("Iniciou listagem dos Tipos de Baixa.")

    ctx = escopo(page)

    select = ctx.locator("select[name='formaOperacao']")
    select.wait_for(state="visible")
    aguardar_ajax_global(page)

    tipos_baixa = []

    for i in range(select.locator("option").count()):
        opcao = select.locator("option").nth(i)
        valor = (opcao.get_attribute("value") or "").strip()
        texto = opcao.inner_text().strip()
        
        if valor and texto:
            tipos_baixa.append(texto)

    logger.info("Finalizou listagem dos Tipos de Baixa. Total: {}.", len(tipos_baixa))
    return tipos_baixa