from loguru import logger
from playwright.async_api import Page

from utils.versao import escopo


def listar_modalidades_baixa(page: Page) -> list[str]:
    logger.info("Iniciou listagem das modalidades da baixa.")

    ctx = escopo(page)

    textos: list[str] = []

    opcoes = ctx.locator("select[name='tipoMovimento'] option")
    opcoes_qtd = opcoes.count()

    for indice_opcao in range(opcoes_qtd):
        opcao = opcoes.nth(indice_opcao)
        valor = (opcao.get_attribute("value") or "").strip()
        texto = opcao.inner_text().strip()
        if not valor or not texto:
            continue
        textos.append(texto)
        logger.debug("Adicionando modalidade de baixa: '{}'", texto)

    logger.info("Finalizou listagem das modalidades da baixa.")
    
    return textos
