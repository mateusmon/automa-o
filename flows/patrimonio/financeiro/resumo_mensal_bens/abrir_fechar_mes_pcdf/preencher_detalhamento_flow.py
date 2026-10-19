from playwright.sync_api import Page, expect
from loguru import logger
from typing import Literal

from utils.waits import preencher_campo, aguardar_ajax_global
from utils.versao import escopo


def preencher_detalhamento(page: Page, ug_data: dict[str, str], operacao: Literal["ABRIR", "FECHAR"] = "FECHAR") -> None:
    ctx = escopo(page)

    logger.info("Iniciou o preenchimento do detalhamento na UG '{}'.", ug_data["nome"])

    logger.info("Preenchendo código da UG: '{}'.", ug_data["codigo"])
    preencher_campo(ctx, "input[name='ugs-1-1']", ug_data["codigo"])
    
    ano_mes_ug = ctx.locator("td[name='ugs-1-2']").text_content()
    assert isinstance(ano_mes_ug, str)

    data = calcular_ano_mes(ano_mes_ug, operacao)

    logger.info("Preenchendo data de fechamento/abertura do mês: '{}'.", data)
    ctx.type("input[name='ugs-1-3']", data, delay=50)
    ctx.type("input[name='ugs1-1-3']", data, delay=50)
    ctx.check("input[name='fecharMes-ugs-fecha-1-4']")
    
    ctx.click("button[name='submitFinish']", timeout=60_000)
    aguardar_ajax_global(page)

    # Esta espera é necessária para a impressão funcionar quando o teste rodar rápido
    expect(ctx.locator("text=Relatórios >> visible=true").first).to_be_visible(timeout=60_000)
    
    logger.info("Finalizou o preenchimento do detalhamento na UG '{}'.", ug_data["nome"])


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
