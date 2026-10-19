from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import clicar_com_ajax, aguardar_ajax_global


def preencher_bens_transferidos_completo(page: Page, funcionario: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento de bens transferidos completo.")

    ctx = escopo(page)
    data = obter_data_patrimonio(page, formato="DDMMYYYY")

    clicar_com_ajax(ctx, "button[name='submitRestore']")

    logger.info("Preenchendo Data de Retorno: '{}'.", data)
    campo_data = ctx.locator("input[name='dtRecebimento-1-5']")
    campo_data.clear()
    campo_data.type(data, delay=50)

    logger.info("Preenchendo Recebedor: '{}'.", funcionario["nome"])
    # Trocar para preencher_campo quando atualizar para versão 3.26
    ctx.locator("input[name='recebedor-1-6']").fill(funcionario["nome"])
    aguardar_ajax_global(page)
    ctx.locator("button[name='lookup-recebedor-1-6']").click()
    aguardar_ajax_global(page)
    linha_funcionario = ctx.locator("table[name='paginationTable'] tbody tr").filter(has_text=funcionario["nome"]).first

    if linha_funcionario.count() == 0:
        raise RuntimeError(f"Funcionário '{funcionario['nome']}' não encontrado na lista de resultados.")

    linha_funcionario.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='consertado-1-7']").click()

    ctx.locator("input[name='vlConserto-1-8']").fill("1000,00")

    logger.info("Preenchendo campo Motivo: 'MOTIVO DE TESTE AUTOMATIZADO'.")
    ctx.locator("input[name='dsMotivo-1-9']").fill("MOTIVO DE TESTE AUTOMATIZADO.")

    logger.info("Preenchendo data inicial de garantia: '{}'.", data)
    campo_inicial = ctx.locator("input[name='dtGarantiaIni-1-10']")
    campo_inicial.clear()
    campo_inicial.type(data, delay=50)

    logger.info("Preenchendo data final de garantia: '{}'.", data)
    campo_final = ctx.locator("input[name='dtGarantiaFim-1-10']")
    campo_final.clear()
    campo_final.type(data, delay=50)

    logger.info("Clicando botão 'Repetir informações'.")
    clicar_com_ajax(ctx, "button[name='submitRepeat-1-11']")

    logger.info("Finalizou o preenchimento de bens transferidos completo.")