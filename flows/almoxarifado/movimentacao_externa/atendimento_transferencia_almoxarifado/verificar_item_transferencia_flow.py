from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def verificar_item_transferencia(page: Page, material: dict[str, str]) -> bool:
    logger.info("Iniciou verificação de itens da transferência para o material {}.", material["nome"])

    ctx = escopo(page)
    resultado = _verificar(ctx, material)

    logger.info("Finalizou verificação de itens da transferência para o material {}.", material["nome"])
    return resultado


def _verificar(ctx, material: dict[str, str]) -> bool:
    linha = ctx.locator(
        'tr[model="model-0"]',
        has=ctx.locator('td[name^="bemServico"]', has_text=material["nome"])
    )

    linha.wait_for(state="visible", timeout=5_000)

    assert linha.count() == 1, (
        f"Esperava apenas 1 linha para o material {material['nome']}, "
        f"mas encontrei {linha.count()} linhas."
    )

    nome_cell = linha.locator('td[name^="bemServico"]')
    estoque_cell = linha.locator('td[name="qtEFLocal"]')

    texto_nome = (nome_cell.text_content() or "").strip()
    estoque = (estoque_cell.inner_text() or "").strip()

    if material["nome"] not in texto_nome:
        logger.info("Material '{}' não encontrado na requisição.", material["nome"])
        return False

    if estoque == "0":
        logger.info("Estoque do material '{}' está zerado.", material["nome"])
        return False

    logger.info("Material '{}' encontrado na requisição com estoque disponível.", material["nome"])
    return True