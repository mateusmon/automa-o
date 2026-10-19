from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.genesis.garantir_enderecamentos.navegar_para_enderecamento_flow import (
    acessar_enderecamento,
)
from flows.genesis.garantir_enderecamentos.verificar_enderecamento_existente_flow import (
    _material_ja_selecionado,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def criar_enderecamento(
    page: Page,
    enderecamentos_faltantes: list[dict[str, Any]],
    unidade_medida_data: dict[str, Any],
) -> None:
    """Cadastra deterministicamente os endereçamentos faltantes na interface."""
    if not enderecamentos_faltantes:
        return

    logger.info(
        f"Iniciando criação de {len(enderecamentos_faltantes)} endereçamento(s)..."
    )

    for item in enderecamentos_faltantes:
        _preencher_formulario_enderecamento(
            page,
            item["almoxarifado"],
            item["material"],
            item["endereco"],
            unidade_medida_data,
        )

    logger.info("Criação de endereçamentos concluída.")


def _preencher_formulario_enderecamento(
    page: Page,
    almoxarifado: dict[str, Any],
    material: dict[str, Any],
    endereco: dict[str, Any],
    unidade_medida: dict[str, Any],
) -> None:
    sigla_almoxarifado = almoxarifado["sigla"]
    nome_material = f"{material['nome']} {material['complemento']}"
    codigo_endereco = endereco["codigo"]
    sigla_um = unidade_medida["sigla"]

    acessar_enderecamento(page)

    ctx = escopo(page)
    is_v3 = get_versao() == 3

    if not _material_ja_selecionado(ctx, nome_material):
        if is_v3:
            campo_almoxarifado = ctx.locator("input[name='almoxarifado']")
            if campo_almoxarifado.is_disabled():
                ctx.locator("button[name='submitNew']").click()
                aguardar_ajax_global(page)
        else:
            ctx.locator("button[name='submitNew']").click()
            aguardar_ajax_global(page)

        preencher_campo(ctx, "input[name='almoxarifado']", sigla_almoxarifado)
        preencher_campo(ctx, "input[name='material']", nome_material)
        aguardar_ajax_global(page)

    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    linhas = ctx.locator("table.tabela tbody tr")

    for i in range(linhas.count()):
        linha = linhas.nth(i)
        campo_endereco = linha.locator("td").nth(2).locator("input[type='text']")
        campo_sigla_um = linha.locator("td").nth(3).locator("input[type='text']")

        if is_v3:
            is_empty = campo_endereco.is_editable() and campo_sigla_um.is_editable()
        else:
            is_empty = (
                campo_endereco.input_value() == ""
                and campo_sigla_um.input_value() == ""
            )

        if is_empty:
            preencher_campo(ctx, campo_endereco, codigo_endereco)
            preencher_campo(ctx, campo_sigla_um, sigla_um)
            break

    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)
