from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    preencher_campo,
)


def efetuar_edicao_requisicao_completa(
    page: Page, almoxarifado: dict[str, str], ur: dict[str, str]
) -> bool:
    logger.info("Iniciou Edição de requisição no almoxarifado '{}'.", almoxarifado["nome"])

    nome_ur = ur["nome"]
    ctx = escopo(page)

    ctx.locator("button[name='submitTabConsulta']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = (
        ctx.locator("table.tabela tr")
        .filter(has=ctx.locator("td").first.filter(has_text=nome_ur))
        .first
    )

    if linha.count() == 0:
        logger.info("Nenhuma requisição pendente encontrada para UR '{}'.", nome_ur)
        return False

    logger.info("Foi encontrada uma requisição pendente para UR '{}'.", nome_ur)
    
    clicar_com_ajax(ctx, linha.get_by_title("Editar"))

    logger.info("Finalizou Edição de requisição no almoxarifado '{}'.", almoxarifado["nome"])
    return True
