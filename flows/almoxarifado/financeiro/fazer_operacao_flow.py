from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_com_refresh
from flows.almoxarifado.financeiro.pendencias.exibir_pendencias_flow import exibir_pendencias

_MAPA_OPERACAO = {
    "ABRIR": "01",
    "FECHAR": "02",
    "ATIVAR": "03",
    "SUSPENDER": "04",
}


def conseguiu_fazer_operacao(page: Page, ug_data: dict, operacao: str) -> bool:
    logger.info("Iniciou operação de ano/mês.")

    ctx = escopo(page)

    linhas = ctx.locator("table.tabela tbody tr")
    linha_ug = linhas.filter(has=ctx.locator(f'input[value*="{ug_data["codigo"]} - {ug_data["nome"]}"]'))

    if linha_ug.count() == 0:
        logger.info("UG '{}' não encontrada na tabela de fechamento de mês.", ug_data["codigo"])
        return False

    if operacao == "PENDÊNCIAS":
        linha_ug.locator("input[name^='verificaPendenciasUg']").click()
        ctx.get_by_role("button", name="Confirmar").click()
        aguardar_ajax_global(page)
        return True

    radio = linha_ug.locator(f"input[name^='cdTpOperacao'][value='{_MAPA_OPERACAO[operacao]}']")
    radio.check()

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)

    if not esperar_com_refresh(ctx, 'a[name="ug-1-2"]'):
        logger.error("Erro ao gerar prova de operação de mês. Verifique se a operação ocorreu corretamente.")
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
        logger.info("Operação feita com sucesso.")
    else:
        logger.info("Operação não foi concluída.")

    return sucesso
