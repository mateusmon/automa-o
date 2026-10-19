import re
from typing import Any

from loguru import logger
from playwright.sync_api import Page, expect

from flows.genesis.garantir_enderecamentos.navegar_para_enderecamento_flow import (
    acessar_enderecamento,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global, preencher_campo


def verificar_enderecamento_existente(
    page: Page,
    almoxarifados_data: list[dict[str, Any]],
    materiais_data: list[dict[str, Any]],
    enderecos_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Percorre a combinação dos itens da massa e retorna os endereçamentos faltantes."""
    logger.info("Iniciando verificação de endereçamentos de material existentes...")

    almoxarifados_total = len(almoxarifados_data)
    materiais_total = len(materiais_data)
    endereco_total = len(enderecos_data)

    enderecamentos_faltantes = []

    for idx_alm, almoxarifado in enumerate(almoxarifados_data, start=1):
        for idx_mat, material in enumerate(materiais_data, start=1):
            # Se for o primeiro material, verifica todos os endereços; se não, apenas o 1º endereço
            enderecos_para_usar = enderecos_data if idx_mat == 1 else enderecos_data[:1]

            for idx_end, endereco in enumerate(enderecos_para_usar, start=1):
                logger.info(
                    "Almoxarifado {}/{}, Material {}/{} e Endereçamento {}/{}",
                    idx_alm,
                    almoxarifados_total,
                    idx_mat,
                    materiais_total,
                    idx_end,
                    endereco_total,
                )

                sigla_almoxarifado = almoxarifado["sigla"]
                nome_material = material["nome"]
                complemento = material["complemento"]
                nome_completo_material = f"{nome_material} {complemento}"
                nome_parcial = f"{nome_material} {complemento.split()[0]}"

                logger.info(
                    "Garantindo endereçamento para material '{}', almoxarifado '{}' e endereço '{}'",
                    nome_parcial,
                    sigla_almoxarifado,
                    endereco["descricao"],
                )

                if _checar_existencia_enderecamento_no_dom(
                    page, sigla_almoxarifado, nome_completo_material, endereco
                ):
                    logger.info(
                        "Endereçamento '{}' para material '{}' e almoxarifado '{}' já existe.",
                        endereco["descricao"],
                        nome_parcial,
                        sigla_almoxarifado,
                    )
                else:
                    logger.info(
                        "Endereçamento '{}' para material '{}' e almoxarifado '{}' não encontrado. Marcado para criação.",
                        endereco["descricao"],
                        nome_parcial,
                        sigla_almoxarifado,
                    )
                    enderecamentos_faltantes.append(
                        {
                            "almoxarifado": almoxarifado,
                            "material": material,
                            "endereco": endereco,
                        }
                    )

    return enderecamentos_faltantes


def _checar_existencia_enderecamento_no_dom(
    page: Page, almoxarifado: str, material: str, endereco: dict[str, Any]
) -> bool:
    """Acessa a tela e consulta a tabela para verificar se o registro existe."""
    acessar_enderecamento(page)

    ctx = escopo(page)

    if get_versao() >= 4:
        ctx.locator("button[name='submitFinish']").wait_for(state="visible")

    is_v3 = get_versao() == 3
    if not _material_ja_selecionado(ctx, material):
        if is_v3:
            campo_almoxarifado = ctx.locator("input[name='almoxarifado']")
            if campo_almoxarifado.is_disabled():
                ctx.locator("button[name='submitNew']").click()
                aguardar_ajax_global(page)
        else:
            ctx.locator("button[name='submitNew']").click()
            aguardar_ajax_global(page)

        preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado)
        if not is_v3:
            expect(ctx.locator("input[name='ug']")).to_have_value(re.compile(r".+"))
        preencher_campo(ctx, "input[name='material']", material)
        aguardar_ajax_global(page)

    tabela = ctx.locator("table.tabela")
    linhas = tabela.locator("tbody tr")

    if get_versao() >= 4:
        try:
            linhas.first.wait_for(state="visible", timeout=1_000)
        except Exception:
            pass

    count = linhas.count()
    if count > 0:
        for i in range(count):
            texto = linhas.nth(i).locator("td").nth(2).locator("input").input_value()
            if " - " in texto:
                partes = texto.split(" - ", 1)
                codigo = partes[0].strip()
                descricao = partes[1].strip()
                if endereco["codigo"] == codigo or endereco["descricao"] == descricao:
                    return True
            else:
                if endereco["codigo"] in texto or endereco["descricao"] in texto:
                    return True

    return False


def _material_ja_selecionado(ctx: Any, material: str) -> bool:
    material_input = ctx.locator("input[name='material']")
    if not material_input.is_visible():
        return False
    val = material_input.input_value()
    return material.lower().strip() in val.lower().strip()
