from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def verificar_existencia_enderecos(page: Page, endereco: str = "endereçado") -> bool:
    logger.info("Iniciou verificação de existência de endereços para o material especificado.")

    ctx = escopo(page)

    campos_endereco = ctx.locator("table.tabela tbody[name='tboItens'] tr td:nth-child(3) input")

    logger.info("Verificando endereço '{}'.", endereco)
    for i in range(campos_endereco.count()):
        valor = campos_endereco.nth(i).input_value()
        if endereco.lower() in valor.lower():
            logger.info("Endereço '{}' encontrado.", endereco)
            logger.info("Finalizou a verificação de existência de endereços para o material especificado.")
            return True

    logger.info("O endereço '{}' não foi encontrado para este material.", endereco)
    return False
