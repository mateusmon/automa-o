import re
from playwright.sync_api import Page, expect
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_status(page: Page, ug_data: dict, timeout_espera=600_000) -> bool | str:
    logger.info("Esperando conclusão da operação na UG '{}'.", ug_data["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)

    linhas = ctx.locator("table.tabela tbody tr")
    linha_ug = linhas.filter(has_text=ug_data["codigo"]).first

    if linha_ug.count() == 0:
        logger.info("UG '{}' não encontrada na tabela de fechamento de mês.", ug_data["codigo"])
        return "UG NÃO ENCONTRADA"

    celula_dt_fim = linha_ug.locator("td[name^='dtFim']")

    try:
        expect(celula_dt_fim).to_have_text(
            re.compile(r"\d{2}/\d{2}/\d{4}"),
            timeout=timeout_espera
        )
    except AssertionError:
        tempo = timeout_espera // 60_000
        logger.warning("Mês em processamento há mais de {} minutos.", tempo)
        return False

    dt_fim = celula_dt_fim.inner_text().strip()
    logger.info("Operação na UG '{}' concluída.", ug_data["nome"])
    return dt_fim
