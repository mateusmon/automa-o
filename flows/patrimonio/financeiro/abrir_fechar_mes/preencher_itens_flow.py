from playwright.sync_api import Page
from loguru import logger
from typing import Literal

from utils.versao import escopo
from utils.waits import preencher_campo, aguardar_ajax_global


def preencher_itens(page: Page, ug_data: dict[str, str], operacao: Literal["ABRIR", "FECHAR"] = "FECHAR") -> None:
    logger.info("Iniciou o preenchimento de itens na UG '{}'.", ug_data["nome"])

    ctx = escopo(page)

    logger.info("Preenchendo código da UG: '{}'.", ug_data["codigo"])
    preencher_campo(ctx, "input[name='ugs-1-1']", ug_data["codigo"])
    
    ano_mes_ug = ctx.locator("span[name='span-1-2']").text_content()
    assert isinstance(ano_mes_ug, str)
    ano_mes_ug = ano_mes_ug.replace("/", "")

    data = calcular_ano_mes(ano_mes_ug, operacao)

    logger.info("Preenchendo data de fechamento/abertura do mês: '{}'.", data)
    campo_data = ctx.locator("input[name='ugs-1-3']")
    campo_data.clear()
    ctx.type("input[name='ugs-1-3']", data, delay=50)
    
    # Aceitando caixa de diálogo para confirmação fechamento de mês
    page.once("dialog", lambda dialog: dialog.accept())
    ctx.click("button[name='submitFinish']", timeout=60_000)
    aguardar_ajax_global(page)
    
    logger.info("Finalizou o preenchimento de itens na UG '{}'.", ug_data["nome"])


def calcular_ano_mes(ano_mes_ug: str, operacao: Literal["ABRIR", "FECHAR"]) -> str:
    if not ano_mes_ug.isdigit():
        raise ValueError(f"ano_mes_ug deve conter apenas dígitos. Recebido: '{ano_mes_ug}'")
    
    if len(ano_mes_ug) != 6:
        raise ValueError(f"ano_mes_ug deve ter 6 dígitos. Recebido: '{ano_mes_ug}'")

    ano = int(ano_mes_ug[:4])
    mes = int(ano_mes_ug[4:])

    if operacao == "ABRIR":
        if mes == 1:
            return f"{ano - 1}12"
        return f"{ano}{mes - 1:02d}"

    # FECHAR: avança para o mês posterior
    if mes == 12:
        return f"{ano + 1}01"
    return f"{ano}{mes + 1:02d}"
