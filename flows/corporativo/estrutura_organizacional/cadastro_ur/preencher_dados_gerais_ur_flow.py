from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais_ur(page: Page, ur: dict) -> None:
    """
    Preenche os dados da UR e confirma o cadastro.

    Cenário A: os mesmos seletores valem para v3 e v4; a única diferença é o
    escopo (page na v3, iframe na v4), resolvido por `escopo(page)`.

    Campos obrigatórios (confirmados ao vivo): U.A. (`cdUa`), Centro de Custo
    (`cdCentroCusto`), Nome (`nmUr`) e Endereço (`cdLocal`). O código da UR é
    gerado pelo sistema (campo desabilitado). A U.G. é preenchida automaticamente
    a partir da U.A.

    :param ur: dict do blueprint com sigla_ua, centro_custo, nome e endereco.
    """
    logger.info("Iniciou preenchimento de dados gerais de UR: '{}'.", ur["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='cdUa']").wait_for(state="visible")

    preencher_campo(ctx, "input[name='cdUa']", ur["sigla_ua"])
    try:
        preencher_campo(ctx, "input[name='cdCentroCusto']", ur["centro_custo"])
    except Exception:
        logger.warning(
            "Não foi possível selecionar o Centro de Custo '{}'. "
            "Cancelando a seleção e tentando o primeiro disponível.",
            ur["centro_custo"],
        )
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        preencher_campo(ctx, "input[name='cdCentroCusto']", "   ")
    logger.info("Preenchendo campos de Nome: '{}'.", ur["nome"])
    ctx.locator("input[name='nmUr']").fill(ur["nome"])
    preencher_campo(ctx, "input[name='cdLocal']", ur["endereco"])
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de UR: '{}'.", ur["nome"])
