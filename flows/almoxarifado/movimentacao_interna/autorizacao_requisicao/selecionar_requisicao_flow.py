from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def _sem_requisicao(ur: dict) -> bool:
    logger.info("Nenhuma requisição encontrada para '{}'.", ur["nome"])
    return False


def selecionar_requisicao(page: Page, ur: dict) -> bool:
    logger.info("Iniciou seleção de requisição na UR '{}'.", ur["nome"])

    ctx = escopo(page)

    if ctx.locator("div[name='divWarningMsg']").is_visible():
        return _sem_requisicao(ur)

    # Existem dois cenários possíveis nesta tela, a depender de quantas
    # requisições pendentes existem no total:
    # (A) Lista genérica de resultados (table[name='paginationTable'] +
    #     span[name='searchResultSize']) — usar "Anexar" (submitUse) na linha
    #     correspondente, que leva à aba "Autorização" com a requisição aberta.
    # (B) Quando há apenas uma requisição pendente, a busca já pula a lista e
    #     abre direto a aba "Autorização", com uma tabela própria de
    #     pendências (uma linha por requisição, cada uma com checkbox
    #     "autoriza") — sem span de contagem nem paginationTable.
    ctx.locator("span[name='searchResultSize'], input[name='autoriza']").first.wait_for(state="visible")

    if ctx.locator("input[name='autoriza']").count() == 0:
        if ctx.locator("span[name='searchResultSize']").inner_text() == "0":
            return _sem_requisicao(ur)

        linha_lista = ctx.locator("table[name='paginationTable'] tbody tr").filter(has_text=ur["nome"]).first
        if linha_lista.count() == 0:
            return _sem_requisicao(ur)

        linha_lista.locator("button[name='submitUse']").click()
        aguardar_ajax_global(page)
        ctx.locator("input[name='autoriza']").first.wait_for(state="visible")

    linha_autorizacao = ctx.locator("table:has(input[name='autoriza']) tbody tr").filter(has_text=ur["nome"]).first

    if linha_autorizacao.count() == 0:
        return _sem_requisicao(ur)

    logger.info("Requisição encontrada na UR '{}', marcando checkbox de autorização.", ur["nome"])
    linha_autorizacao.locator("input[name='autoriza']").check()

    logger.info("Finalizou seleção de requisição na UR '{}'.", ur["nome"])
    return True
