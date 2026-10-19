from loguru import logger
from playwright.sync_api import Page

from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.navegar_para_almoxarifado_flow import (
    acessar_almoxarifado,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def criar_almoxarifado(
    page: Page, almoxarifados_faltantes: list[dict], sigla_ug: str
) -> None:
    """Itera e cria os almoxarifados recebidos na lista de faltantes."""
    if not almoxarifados_faltantes:
        logger.info("Nenhum almoxarifado a ser criado.")
        return

    total = len(almoxarifados_faltantes)
    logger.info("Iniciando a criação de {} almoxarifado(s)...", total)

    for atual, almoxarifado in enumerate(almoxarifados_faltantes, start=1):
        logger.info(
            "Criando almoxarifado {}/{} - Nome: '{}'",
            atual,
            total,
            almoxarifado["nome"],
        )
        _criar_almoxarifado_individual(
            page=page,
            almoxarifado_data=almoxarifado,
            sigla_ug=sigla_ug,
        )

    logger.info("Todos os almoxarifados faltantes foram criados.")


def _criar_almoxarifado_individual(
    page: Page, almoxarifado_data: dict, sigla_ug: str
) -> None:
    """Realiza a criação preenchendo o formulário de um único almoxarifado."""
    nome_almoxarifado = almoxarifado_data["nome"]
    sigla_almoxarifado = almoxarifado_data["sigla"]

    acessar_almoxarifado(page)

    ctx = escopo(page)

    if ctx.locator("input[name='cdAlmoxarifado']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='dsAlmoxarifado']").fill(nome_almoxarifado)
    ctx.locator("input[name='sgAlmoxarifado']").fill(sigla_almoxarifado)

    ctx.locator("input[name='inControleFin'][value='S']").check()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='cdUg']", sigla_ug)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
