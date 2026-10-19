from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, preencher_campo


def validar_botoes_comuns(page: Page, ul: dict[str, str]) -> None:
    logger.info("Iniciou validação dos botões comuns.")

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ulDestino']", ul["sigla"])

    logger.debug("Iniciou verificação dos botões da aba 'Dados Gerais'")
    _clicar_botoes_comuns(page, ul)

    logger.debug("Iniciou verificação dos botões da aba 'Itens'")
    _clicar_botoes_comuns(page, ul, "itens")

    logger.debug("Iniciou verificação dos botões da aba 'Observações'")
    _clicar_botoes_comuns(page, ul, "observações")

    logger.info("Finalizou validação dos botões comuns.")


def _clicar_botoes_comuns(page: Page, ul, aba: str = "dados gerais") -> None:

    ctx = escopo(page)

    if aba == "itens":
        clicar_com_ajax(ctx, "button[name='submitTabItens']")
    elif aba == "observações":
        clicar_com_ajax(ctx, "button[name='submitTabObservacoes']")

    # Verificar botão de visualização
    logger.debug("Iniciou verificação do botão de 'Visualização'")
    clicar_com_ajax(ctx, "button[name='submitView']")
    expect(ctx.locator("button[name='submitTabVisualizacao']")).to_be_visible()
    expect(ctx.locator("span[bind='ulDestino']")).not_to_have_text("")
    ctx.wait_for_timeout(3_000)
    clicar_com_ajax(ctx, "button[name='submitBack']")
    logger.debug("Finalizou verificaçõa do botão de 'Visualização'")
 

    # Verificar botão de restaurar
    logger.debug("Iniciou verificação do botão de 'Restaurar'")
    clicar_com_ajax(ctx, "button[name='submitRestore']")
    expect(ctx.locator("input[name='ulDestino']")).to_have_text("")
    logger.debug("Finalizou verificaçõa do botão de 'Restaurar'")

    # Verificar botão de consulta
    logger.debug("Iniciou verificação do botão de 'Consulta'")
    preencher_campo(ctx, "input[name='ulDestino']", ul["sigla"])
    if aba == "itens":
        clicar_com_ajax(ctx, "button[name='submitTabItens']")
    elif aba == "observações":
        clicar_com_ajax(ctx, "button[name='submitTabObservacoes']")   
    clicar_com_ajax(ctx, "button[name='submitSearch']")
    titulo_tabela = ctx.locator("table[name='paginationTable'] caption")
    expect(titulo_tabela).to_be_visible()
    # Tempo para verificar se foi para a página correta
    ctx.wait_for_timeout(3_000)
    clicar_com_ajax(ctx, "button[name='submitCancel']")
    logger.debug("Finalizou verificaçõa do botão de 'Consulta'")

    # Verificar botão de novo
    logger.debug("Iniciou verificação do botão de 'Novo'") 
    clicar_com_ajax(ctx, "button[name='submitNew']")
    expect(ctx.locator("input[name='ulDestino']")).to_have_text("")
    logger.debug("Finalizou verificaçõa do botão de 'Novo'")

    preencher_campo(ctx, "input[name='ulDestino']", ul["sigla"])
    aguardar_ajax_global(page)
