from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_estorno_baixa_bens(page: Page, justificativa: str = "Justificativa Nova.")-> bool:
    logger.info("Alterando estorno da baixa de bens {}.", justificativa)

    ctx = escopo(page)

    # Preenche justificativa
    logger.info("Preenchendo justificativa do estorno da baixa de bens com '{}'.", justificativa)
    ctx.locator("textarea[name='txJustBaixaEstorno']").fill(justificativa)

    linhas = ctx.locator("table[name='paginationTable'] tbody tr")
    total = linhas.count()

    # Só é possível fazer uma alteração na justificativa se uma data for adicionada em um item
    # a ser estornado. Se o item tem o campo de data desabilitado, é porque já há uma data 
    # estabelecida para ele. Nesse caso é necessário alterar a data do próximo item, se houve,
    # e se o campo de data dele estiver habilitado.
    for i in range(total):
        linha = linhas.nth(i)
        celula = linha.locator("input[name^='dtEstorno-']")
        if celula.is_enabled():
            data=obter_data_patrimonio(page, "DD/MM/YYYY")
            celula.fill(data)
            aguardar_ajax_global(page)
            break
    else:
        logger.info("Esse estorno não pode ser alterado pois a baixa não possui mais itens a serem estornados")
        return False
    
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Estorno da Baixa de Bens alterado. Justificativa: '{}'.", justificativa)
    return True
