from loguru import logger
from playwright.async_api import Page

from utils.versao import escopo


def listar_situacoes_baixa(page: Page) -> list[str]:
    logger.info("Iniciou listagem das situacoes da baixa.")

    ctx = escopo(page)
    
    select = ctx.locator("select[name='tipoSituacaoBaixa']")
    select.wait_for(state="visible")

    if select.is_disabled():
        logger.warning("Ccampo de situação da baixa está desabilitada")
        return []

    textos: list[str] = []

    opcoes = ctx.locator("select[name='tipoSituacaoBaixa'] option")
    opcoes_qtd = opcoes.count()

    for indice_opcao in range(opcoes_qtd):
        opcao = opcoes.nth(indice_opcao)
        valor = (opcao.get_attribute("value") or "").strip()
        texto = opcao.inner_text().strip()
        if not valor or not texto:
            continue
        textos.append(texto)
        logger.debug("Adicionando situação de baixa: '{}'", texto)

    logger.info("Finalizou listagem das situacoes da baixa.")
    
    return textos
