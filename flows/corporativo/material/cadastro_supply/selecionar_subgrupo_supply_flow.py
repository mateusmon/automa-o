from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_subgrupo_supply(page: Page, supply: dict) -> bool:
    """
    Marca o radio (`sgSel`) do material do subgrupo carregado, o que prepara a exclusão do
    subgrupo. Cenário A. Pressupõe que o subgrupo já foi carregado (ver
    `consultar_subgrupo_supply`).

    :param supply: dict do blueprint (não utilizado além de manter a assinatura padrão).
    :return: True se o material foi encontrado e marcado; False caso contrário (nada a excluir).
    """
    logger.info("Iniciou seleção de subgrupo do Supply.")

    ctx = escopo(page)

    radio = ctx.locator("input[name='sgSel']")

    if radio.count() == 0:
        logger.info("Nenhum subgrupo carregado para exclusão.")
        return False

    radio.first.check()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de subgrupo do Supply.")
    return True
