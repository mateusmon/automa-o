from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_com_refresh
from flows.almoxarifado.financeiro.pendencias.exibir_pendencias_flow import exibir_pendencias


def conseguiu_fechar_mes(page: Page, ug_data: dict) -> bool:
    logger.info("Iniciou o fechamento de mês.")

    ctx = escopo(page)

    linhas = ctx.locator("table.tabela tbody tr")

    logger.info("Procurando UG '{}' na tabela de fechamento de mês.", ug_data["codigo"])
    linha_ug = linhas.filter(has=ctx.locator(f'input[value*="{ug_data["codigo"]} - {ug_data["nome"]}"]'))

    if linha_ug.count() == 0:
        logger.info("UG '{}' não encontrada na tabela de fechamento de mês.", ug_data["codigo"])
        return False

    radio = linha_ug.locator("input[name^='cdTpOperacao'][value='02']")
    radio.check()

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)

    if not esperar_com_refresh(ctx, 'a[name="ug-1-2"]', timeout_total_sec=600):
        logger.error("Erro ao gerar prova de fechamento de mês. Verifique se o mês foi fechado corretamente.")
        return False

    with page.expect_popup() as popup_info:
        ctx.locator('a[name="ug-1-2"]').click()

    resultado = popup_info.value
    resultado.wait_for_load_state("load")

    sucesso = "Sucesso" in resultado.locator("body").inner_text()
    pagina_pendencias = "Financeiro" in resultado.locator("body").inner_text()

    if pagina_pendencias:
        exibir_pendencias(resultado)

    resultado.close()

    if sucesso:
        logger.info("Mês fechado com sucesso.")
    else:
        logger.info("Mês não foi fechado.")

    return sucesso
