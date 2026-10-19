from datetime import date, datetime

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def atender_requisicao(page: Page, material: dict[str, str] | None = None) -> bool:
    logger.info("Iniciou atendimento de requisição.")

    ctx = escopo(page)

    data_aberta_str = obter_data_almoxarifado(page, "DD/MM/YYYY")
    data_aberta = datetime.strptime(data_aberta_str, "%d/%m/%Y").date()
    data_hoje = date.today()

    if data_hoje > data_aberta:
        logger.warning(
            f"Atendimento interrompido: a data de hoje ({data_hoje.strftime('%d/%m/%Y')}) "
            f"é posterior à data aberta no almoxarifado ({data_aberta_str})."
        )
        return False

    logger.info("Preenchendo data de atendimento: '{}'.", data_aberta_str)
    ctx.locator("input[name='dtConfirmada']").fill(data_aberta_str)

    linhas = ctx.locator('tr[model^="model-"]').all()

    for index, linha in enumerate(linhas, start=1):
        linha.wait_for(state="visible")

        td_qt_requisicao = linha.locator('td[name="qtRequisicao"]')
        qt_requisicao_texto = td_qt_requisicao.inner_text().strip()

        input_qt_atendido = linha.locator('input[name^="qtAtendido"]')

        if input_qt_atendido.is_visible() and input_qt_atendido.is_enabled():
            logger.info("Preenchendo quantidade atendida para a linha {}: '{}'.", index, qt_requisicao_texto)
            input_qt_atendido.fill(qt_requisicao_texto)

    botao_confirmar = ctx.get_by_role("button", name="Confirmar")
    clicar_com_ajax(ctx, botao_confirmar)
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou atendimento de requisição.")
    return True
