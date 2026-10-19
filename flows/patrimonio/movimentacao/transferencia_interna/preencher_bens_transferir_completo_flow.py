from loguru import logger
from playwright.sync_api import Page

from flows.patrimonio.shared.consultar_bem_flow import consultar_bem
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def preencher_bens_transferir_completo(page: Page, ug: dict[str, str], material: dict[str, str]) -> bool | str:
    logger.info("Iniciou o preenchimento dos bens.")

    ctx = escopo(page)
    
    clicar_com_ajax(ctx, "button[name='submitTabItens']")

    linhas = ctx.locator("table.tabelaComRolagem tbody tr")

    if linhas.count() == 0 and ctx.locator("button[name='submitAddLine1']").is_disabled():
        logger.warning("Não é possível preencher bens para transferência. Pulando flow.")
        return
    elif linhas.count() == 0:
        clicar_com_ajax(ctx, "button[name='submitAddLine1']")

    # Verificar botões de adição e subtração de linhas
    ctx.locator("input[name='dsOcorrencia-1-7']").fill("OCORRÊNCIA TESTE")
    clicar_com_ajax(ctx, "button[name='lookup-nrPatrAntigo-1-4']")
    bem_encontrado = consultar_bem(page, ug, material)
    if not bem_encontrado:
        logger.info("Bem não encontrado")
        botao_cancelar = ctx.locator("button[name='submitCancel']").first
        clicar_com_ajax(ctx, botao_cancelar)

    aguardar_ajax_global(page)

    ctx.locator("input[name='submitMarkAll1']").check()
    clicar_com_ajax(ctx, "button[name='submitPurgeLines1']")
    quantidade_subtracao = linhas.count()

    if quantidade_subtracao != 0:
        logger.warning("Botão de subtração de linhas não funcionou corretamente. Verificar manualmente.")

    clicar_com_ajax(ctx, "button[name='submitAddLine1']")

    quantidade_adicao = linhas.count()

    if quantidade_adicao == 0:
        logger.warning("Botão de adição de linhas não funcionou corretamente. Verificar manualmente.")

    ctx.locator("input[name='dsOcorrencia-1-7']").fill("OCORRÊNCIA TESTE")
    clicar_com_ajax(ctx, "button[name='lookup-cdBemPerm-1-3']")
    encontrou_bem = consultar_bem(page, ug, material)

    if not encontrou_bem:
        logger.info("Bem não encontrado.")
        return False


    clicar_com_ajax(ctx, "button[name='submitLookupAll']")

    logger.info("Finalizou o preenchimento dos bens.")
    return True
