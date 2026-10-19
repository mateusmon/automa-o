from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def selecionar_subgrupo(page: Page, material: dict[str, str]) -> None:
    """
    Seleciona o subgrupo no cadastro de material (form `bemser`, compartilhado por
    Consumo/Permanente/Serviço). Cenário A (escopo via `escopo(page)`).

    Preenche o código do subgrupo (`material["subgrupo"]`) e clica no ícone "Retornar"
    da linha no painel de classificação. Se o subgrupo não existir, cai na Tabela
    Federal Supply e o seleciona pela árvore.

    :param material: dict do blueprint (usa a chave `subgrupo`).
    """
    subgrupo = material["subgrupo"]
    logger.info("Iniciou seleção de subgrupo '{}'.", subgrupo)

    ctx = escopo(page)
    preencher_campo(ctx, "input[name='subgrupo']", subgrupo)

    aviso = ctx.locator("text=Nenhum SUBGRUPO encontrado!")
    retornar = ctx.locator("img[title='Retornar']").first
    expect(aviso.or_(retornar)).to_be_visible()

    if aviso.is_visible():
        ctx.locator(".x-btn-center button:has-text('OK')").click()
        aguardar_ajax_global(page)
        ctx.locator("button[name='federalSupply']").click()
        aguardar_ajax_global(page)
        logger.info("Subgrupo '{}' não encontrado. Selecionando na Tabela Federal Supply.", subgrupo)
        ctx.locator("input[name='filtro']").fill(subgrupo)
        ctx.locator("button[name='lookup-filtro']").click()
        aguardar_ajax_global(page)
        ctx.locator("img.x-tree-node-icon.icon-subgrupo-open").dblclick()
        aguardar_ajax_global(page)
    else:
        retornar.click()
        aguardar_ajax_global(page)

    logger.info("Finalizou seleção de subgrupo. '{}'.", subgrupo)
