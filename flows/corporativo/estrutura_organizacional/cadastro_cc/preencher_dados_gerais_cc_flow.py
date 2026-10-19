from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais_cc(page: Page, centro_custo: dict) -> bool:
    """
    Preenche o Centro de Custos e confirma o cadastro.

    Cenário A: os mesmos seletores valem para v3 e v4; a única diferença é o
    escopo (page na v3, iframe na v4), resolvido por `escopo(page)`.

    Único campo editável obrigatório: Nome (`nmCentroCusto`). O Órgão vem
    pré-preenchido e o Código é gerado pelo sistema.

    :param centro_custo: dict do blueprint com nome.
    :return: False quando o botão Confirmar está desabilitado; True após confirmar.
    """
    logger.info("Iniciou preenchimento de dados gerais de CC - Centro de Custos '{}'.", centro_custo["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmCentroCusto']").wait_for(state="visible")

    logger.info("Preenchendo campo de Nome do CC - Centro de Custos com '{}'.", centro_custo["nome"])
    ctx.locator("input[name='nmCentroCusto']").fill(centro_custo["nome"])

    botao_confirmar = ctx.locator("button[name='submitFinish']")
    if botao_confirmar.is_disabled():
        logger.info("Botão Confirmar desabilitado para o cadastro de Centro de Custos.")
        return False

    botao_confirmar.click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de CC - Centro de Custos '{}'.", centro_custo["nome"])
    return True
