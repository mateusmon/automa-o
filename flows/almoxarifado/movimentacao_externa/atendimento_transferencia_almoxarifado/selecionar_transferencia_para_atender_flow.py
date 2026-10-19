from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_transferencia(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de transferência para atendimento no almoxarifado {}.", almoxarifado["nome"])

    ctx = escopo(page)
    resultado = _selecionar(ctx, page, almoxarifado)

    logger.info("Finalizou seleção de transferência para atendimento no almoxarifado {}.", almoxarifado["nome"])
    return resultado


def _selecionar(ctx, page: Page, almoxarifado: dict[str, str]) -> bool:
    linhas = ctx.locator("table.tabelaComRolagem tbody tr")

    campo_total = ctx.locator("input[name='qtdRequisicoes']")
    expect(campo_total).to_be_visible()

    if campo_total.input_value().strip() == "0":
        logger.info("Nenhuma transferência encontrada para '{}'.", almoxarifado["nome"])
        return False

    for i in range(linhas.count()):
        linha = linhas.nth(i)
        texto_celula = linha.locator("td").nth(4).text_content() or ""
        texto_celula = texto_celula.strip()

        partes = texto_celula.split(" - ", 1)
        if len(partes) < 2:
            continue

        nome_almoxarifado_linha = partes[1]

        if nome_almoxarifado_linha in almoxarifado["nome"]:
            logger.debug("Transferência encontrada para o almoxarifado '{}' na linha {}.", almoxarifado["nome"], i)
            linha.locator("td").nth(6).locator("input[type=checkbox]").check()
            break
    else:
        logger.info("Nenhuma transferência encontrada para o almoxarifado '{}'.", almoxarifado["nome"])
        return False

    ctx.locator("button[name='submitTabAtendimento']").click()
    aguardar_ajax_global(page)

    return True
