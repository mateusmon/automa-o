from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_basicos_endereco(page: Page, endereco: dict) -> None:
    """
    Preenche o Endereço com a mesma sequência da criação legada (`_criar_endereco`):
    se a tela já tiver dados carregados (campo Instalação preenchido), clica em "Novo"
    para não sobrescrever o registro anterior; depois preenche Nome → Instalação
    (lookup) e confirma.

    :param endereco: dict do blueprint (nome, instalacao).
    """
    logger.info("Iniciou preenchimento de dados básicos de Endereço '{}'.", endereco["nome"])

    ctx = escopo(page)

    if ctx.locator("input[name='instalacao']").input_value() != "":
        logger.info("Tela com dados carregados. Clicando em 'Novo' antes de preencher.")
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='nmLocal']").fill(endereco["nome"])

    preencher_campo(ctx, "input[name='instalacao']", endereco["instalacao"])

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados básicos de Endereço '{}'.", endereco["nome"])
