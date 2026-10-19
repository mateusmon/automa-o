from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_bens(page: Page, ul: dict[str, str]) -> str | bool:
    """
    Seleciona um bem na tabela de resultados para realizar associação.

    A função verifica se existem pelo menos dois bens cadastrados na UL
    informada. Caso não haja quantidade suficiente, o teste é interrompido
    e a função retorna False.

    Quando há dois ou mais bens, obtém o número patrimonial do penúltimo
    registro da tabela, seleciona o último bem disponível por meio do botão
    "Usar" e retorna o número patrimonial capturado.

    Args:
        page: Instância da página do Playwright.
        ul: Dicionário contendo os dados da Unidade de Localização (UL),
            incluindo a chave "sigla" utilizada para registro em log.

    Returns:
        O número patrimonial (str) do bem selecionado para associação,
        ou False caso não existam bens suficientes na UL.
    """
    logger.info("Iniciou a seleção de bens para a UL '{}'.", ul["sigla"])

    ctx = escopo(page)

    rows = ctx.locator("table.tabela").first.locator("tbody tr")
    count = rows.count()

    if count < 2:
        logger.info(
            "Deve haver pelo menos dois bens na UL '{}' para fazer a associação. "
            "Não há bens suficientes", ul["sigla"]
        )
        logger.info("Pulando teste.")
        return False
    
    num_patrim = rows.nth(count-2).locator("td").nth(2).inner_text()

    rows.last.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    
    logger.info("Finalizou a seleção de bens {}.", num_patrim)
    return num_patrim
