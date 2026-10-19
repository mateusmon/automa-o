from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preencher_itens(
    page: Page, material: dict, quantidade: str | int, teste_linha: bool = False
) -> bool:
    logger.info("Iniciou preenchimento da tabela 'Itens'.")

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"
    quantidade = int(quantidade)

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    ctx.locator("input[name='cdBemServico-1-2']").fill(nome_completo_material)
    aguardar_ajax_global(page)
    ctx.locator("button[name='lookup-cdBemServico-1-2']").click()
    aguardar_ajax_global(page)

    linhas = ctx.locator("tr[name='searchResultData']")
    count = linhas.count()
    for i in range(count):
        linha = linhas.nth(i)
        classificacao = (
            linha.locator("td[bind='naturezaClas']").inner_text().strip().upper()
        )
        if classificacao == "ESTOCÁVEL":
            linha.locator("button.btnAnexar").click()
            aguardar_ajax_global(page)
            break

    quantidade_input = int(ctx.locator("input[name='qtEstoque-2-5']").input_value().replace(".", ""))

    if quantidade > quantidade_input:
        logger.info(
            "Quantidade solicitada ('{}') maior que o estoque disponível ('{}').",
            quantidade,
            quantidade_input,
        )
        return False

    logger.info("Preenchendo quantidade de baixa: '{}'.", quantidade)
    ctx.locator("input[name^='qtBaixa-2']").fill(str(quantidade))
    _preencher_lote(ctx, page, str(quantidade))

    if teste_linha == True:
        ctx.locator("button[name='submitAddLine1']").click()
        aguardar_ajax_global(page)
        ctx.locator("button[name='submitPurgeLines1']").click()
        aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento da tabela 'Itens'.")
    return True


def _preencher_lote(ctx, page: Page, quantidade: str) -> None:
    botao_acoes = ctx.locator("button[name='edit-itens-2-7']")

    if botao_acoes.is_visible() and botao_acoes.is_enabled():
        logger.info("Preenchendo lote.")

        botao_acoes.click()
        aguardar_ajax_global(page)

        logger.info("Preenchendo quantidade de lote: '{}'.", quantidade)
        ctx.locator("input[name='qtLote-1-6']").fill(quantidade)

        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)
