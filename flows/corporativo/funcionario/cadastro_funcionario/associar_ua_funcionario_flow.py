from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def associar_ua_funcionario(page: Page, ua: dict) -> None:
    """
    Abre o Funcionário da consulta atual (já filtrada por CPF), preenche a U.A. pela
    sigla via lookup (`lookup-ccdUa`) e confirma — mesma sequência da criação legada
    (`_criar_associacao_funcionario_ua`).

    :param ua: dict do blueprint (usa a chave `sigla`).
    """
    logger.info("Iniciou associação do Funcionário à U.A. '{}'.", ua["sigla"])

    ctx = escopo(page)

    ctx.wait_for_selector("table[name='paginationTable']")
    ctx.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='cdUa']", ua["sigla"], lookup_name="lookup-ccdUa")

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou associação do Funcionário à U.A. '{}'.", ua["sigla"])
