from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def verificar_item_requisicao(page: Page, material: dict[str, str]) -> bool:
    logger.info("Verificando material '{}' da requisição.", material["nome"])

    ctx = escopo(page)

    linha = ctx.locator('tr[model="model-0"]', has=ctx.locator('td[name^="bemServico"]', has_text=material["codigo"]))

    linha.wait_for(state="visible", timeout=1_000)
    qtd_linhas = linha.count()

    if qtd_linhas > 1:
        logger.info("Esperava apenas 1 linha para o material {}, mas encontrou {} linhas.", material["nome"], qtd_linhas)
        return False

    codigo_cell = linha.locator('td[name^="bemServico"]')
    estoque_cell = linha.locator('td[name="qtEFLocal"]')

    texto_nome = (codigo_cell.text_content() or "").strip()
    estoque = (estoque_cell.inner_text() or "").strip()

    if material["nome"] not in texto_nome:
        logger.info("Material '{}' não encontrado na requisição.", material["nome"])
        return False

    if estoque == "0":
        logger.info("Estoque do material '{}' está zerado.", material["nome"])
        return False

    logger.info("Material '{}' da requisição verificado.", material["nome"])
    return True
