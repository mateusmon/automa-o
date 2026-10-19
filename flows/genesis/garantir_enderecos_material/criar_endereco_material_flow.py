from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.almoxarifado.auxiliares.endereco_estoque.navegar_para_endereco_estoque_flow import (
    acessar_endereco_estoque,
)
from utils.versao import escopo, get_versao
from utils.waits import (
    aguardar_ajax_global,
    esperar_pagina_carregar,
    esperar_sucesso_ou_erro,
    preencher_campo,
)


def criar_endereco_material(
    page: Page, enderecos_faltantes: list[dict[str, Any]]
) -> None:
    """Realiza o cadastro determinístico de todos os endereços pendentes."""
    if not enderecos_faltantes:
        return

    logger.info(
        f"Iniciando criação de {len(enderecos_faltantes)} endereço(s) de estoque..."
    )

    for item in enderecos_faltantes:
        almoxarifado = item["almoxarifado"]
        endereco = item["endereco"]
        logger.info(
            "Criando endereço '{}' no almoxarifado '{}'...",
            endereco["descricao"],
            almoxarifado["sigla"],
        )
        _preencher_formulario_endereco(page, endereco, almoxarifado)

    logger.info("Criação de endereços de estoque concluída.")


def _preencher_formulario_endereco(
    page: Page, endereco: dict[str, Any], almoxarifado_data: dict[str, Any]
) -> None:
    """Preenche os campos da interface para criar um endereço de estoque."""
    codigo_endereco = endereco["codigo"]
    descricao_endereco = endereco["descricao"]
    sigla_endereco = endereco["sigla"]
    sigla_almoxarifado = almoxarifado_data["sigla"]

    acessar_endereco_estoque(page)

    ctx = escopo(page)

    if ctx.locator("input[name='almoxarifado']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='almoxarifado']", sigla_almoxarifado)

    codigo_input = ctx.locator("input[name='cdEndereco']")
    if codigo_input.is_enabled():
        codigo_input.fill(codigo_endereco)

    ctx.locator("input[name='dsEnderecoEst']").fill(descricao_endereco)
    ctx.locator("input[name='sgEnderecoEst']").fill(sigla_endereco)

    ctx.locator("input[name='idUltNivel']").check()

    ctx.get_by_role("button", name="Confirmar").click()

    if get_versao() >= 4:
        aguardar_ajax_global(page)
        esperar_sucesso_ou_erro(ctx)
    else:
        esperar_pagina_carregar(page)
        esperar_sucesso_ou_erro(page)
