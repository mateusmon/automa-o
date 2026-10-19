from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    clicar_com_ajax,
    esperar_sucesso_ou_erro,
    select_tipo,
)


def preencher_dados_gerais(page: Page, operacao: str, nome: str):
    logger.info("Preenchendo dados gerais da operação '{}' de tipo '{}'.", nome, operacao)

    ctx = escopo(page)

    # Selecionar operação
    logger.info("Selecionando tipo de operação: '{}'.", operacao)
    select_tipo(ctx, "tipoOperacao", operacao)

    # Preencher Tipo de Operação
    logger.info("Preenchendo nome da operação: '{}'.", nome)
    ctx.locator("input[name='nmTpFormaOp']").fill(nome)

    clicar_com_ajax(ctx, "button[name='submitFinish']")

    try:
        esperar_sucesso_ou_erro(ctx)       
    except RuntimeError as e:
        mensagem_erro = str(e).lower()
        termos_skip = ["cadastrada"]
        if any(termo in mensagem_erro for termo in termos_skip):
            logger.warning("Operação '{}' de tipo '{}' já cadastrada.", nome, operacao)
            return False
        raise

    logger.info("Dados gerais da operação '{}' de tipo '{}' preenchidos.", nome, operacao)
    return True