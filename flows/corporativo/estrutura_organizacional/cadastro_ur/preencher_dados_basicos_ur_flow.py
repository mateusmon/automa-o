from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_basicos_ur(page: Page, ur: dict) -> None:
    """
    Preenche a UR com a mesma sequência da criação legada (`_criar_ur`):
    se a tela já tiver dados carregados (campo U.G. preenchido), clica em "Novo"
    para não sobrescrever o registro anterior; depois preenche U.A. → Centro de
    Custo (somente se o campo estiver habilitado) → Nome → Endereço e confirma.

    :param ur: dict do blueprint (sigla_ua, centro_custo, nome, endereco).
    """
    logger.info("Iniciou preenchimento de dados básicos de UR '{}'.", ur["nome"])

    ctx = escopo(page)

    if ctx.locator("input[name='cdUg']").input_value() != "":
        logger.info("Tela com dados carregados. Clicando em 'Novo' antes de preencher.")
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='cdUa']", ur["sigla_ua"])

    try:
        if ctx.locator("input[name='cdCentroCusto']").is_enabled():
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

    ctx.locator("input[name='nmUr']").fill(ur["nome"])

    preencher_campo(ctx, "input[name='cdLocal']", ur["endereco"])

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados básicos de UR '{}'.", ur["nome"])
