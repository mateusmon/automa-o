import re

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def listar_tipos_bem(page: Page) -> list[str]:
    """
    Lista o texto de todos os Tipos de Bem disponíveis no <select> 'tipoBem'
    da Entrada de Bens. Chamar DEPOIS de `preencher_ug` — as opções dependem
    da UG selecionada. Ignora a opção em branco/placeholder.
    """
    logger.info("Iniciou listagem dos Tipos de Bem.")

    ctx = escopo(page)

    textos: list[str] = []

    select = ctx.locator("select[name='tipoBem']")
    select.wait_for(state="visible")
    aguardar_ajax_global(page)

    select.locator("option").filter(has_text=re.compile(r"\S")).first.wait_for(state="attached")
    
    opcoes = select.locator("option")

    for i in range(opcoes.count()):
        opcao = opcoes.nth(i)
        valor = (opcao.get_attribute("value") or "").strip()
        texto = opcao.inner_text().strip()
        if not valor or not texto:
            continue
        textos.append(texto)

    logger.info("Finalizou listagem dos Tipos de Bem. Total: {}.", len(textos))
    return textos
