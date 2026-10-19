import re

from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def listar_formas_operacao(page: Page) -> list[str]:
    """
    Lista o texto de todas as Formas de Operação disponíveis no <select>
    'tipoBemFormaOperacao'. As opções dependem do Tipo de Bem já
    selecionado — chamar DEPOIS de `escolher_tipo_bem`. Ignora a opção em
    branco/placeholder.
    """
    logger.info("Iniciou listagem das Formas de Operação.")

    page.wait_for_load_state("domcontentloaded")
    aguardar_ajax_global(page)

    ctx = escopo(page)

    select = ctx.locator("select[name='tipoBemFormaOperacao']")
    select.wait_for(state="visible")
    aguardar_ajax_global(page)

    select.locator("option").filter(has_text=re.compile(r"\S")).first.wait_for(state="attached")
    
    opcoes  = ctx.locator("select[name='tipoBemFormaOperacao']").locator("option")

    textos: list[str] = []
    for i in range(opcoes.count()):
        opcao = opcoes.nth(i)
        valor = (opcao.get_attribute("value") or "").strip()
        texto = opcao.inner_text().strip()
        if not valor or not texto:
            continue
        textos.append(texto)

    logger.info("Finalizou listagem das Formas de Operação. Total: {}.", len(textos))
    return textos
