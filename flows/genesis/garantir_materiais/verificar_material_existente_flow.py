from typing import Any

from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def verificar_material_existente(
    page: Page, materiais_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Identifica quais itens da massa ainda não existem na tela de materiais já aberta."""
    logger.info("Iniciando verificação de materiais existentes...")

    total = len(materiais_data)
    logger.info("Foi encontrado um total de {} materiais no arquivo yaml.", total)

    materiais_faltantes = []

    for atual, material in enumerate(materiais_data, start=1):
        logger.info("Verificando material {}/{}", atual, total)
        nome = material["nome"]

        logger.info("Garantindo material nome '{}'", nome)

        if _checar_existencia_material_no_dom(page, nome):
            logger.info("Material '{}' já existe. Nenhuma ação necessária.", nome)
        else:
            logger.info("Material '{}' não encontrado. Marcado para criação.", nome)
            materiais_faltantes.append(material)

    return materiais_faltantes


def _checar_existencia_material_no_dom(page: Page, nome_material: str) -> bool:
    """Realiza a consulta no modal do sistema e verifica se o material existe."""
    ctx = escopo(page)

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)

    # Preenche a busca pelo nome
    campo_bem = ctx.locator("textarea[name='complemento_NmBemServico']")
    campo_bem.fill(nome_material)
    aguardar_ajax_global(page)

    # Dispara atualização. Cenário B: na v4 o breadcrumb fica fora do iframe.
    if get_versao() >= 4:
        page.get_by_role("heading", name="Material - Consumo").click()
    else:
        ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    # Clica na lupa de pesquisa e aguarda o painel
    for tentativa in range(3):
        ctx.locator("button[name='lookup-complemento_NmBemServico']").click(
            no_wait_after=True
        )
        aguardar_ajax_global(page)
        try:
            ctx.locator("select[name='tpFil']").wait_for(state="visible", timeout=1_000)
            break
        except Exception:
            if tentativa == 2:
                raise RuntimeError(
                    "Painel de busca de bem não abriu após 3 tentativas."
                )
            aguardar_ajax_global(page)

    # Trata modal de alerta de COMPLEMENTO, se houver
    erro = ctx.locator(".ext-mb-text")
    resultado_grid = ctx.locator(".x-grid3-cell-inner.x-grid3-col-material").first
    expect(erro.or_(resultado_grid)).to_be_visible(timeout=30_000)

    if erro.is_visible():
        if "COMPLEMENTO" in erro.inner_text():
            ctx.locator(".x-window-dlg button.x-btn-text", has_text="OK").click()
            aguardar_ajax_global(page)
            ctx.locator(".ext-el-mask").wait_for(state="hidden")

    # Filtra por Bem
    ctx.select_option("select[name='tpFil']", value="tpFiltroMaterial")
    ctx.locator("button[name='lookup-filtro']").click()
    aguardar_ajax_global(page)

    # Avalia resultado da consulta
    erro = ctx.locator(".ext-mb-text")
    resultado_grid = ctx.locator(".x-grid3-cell-inner.x-grid3-col-material").first
    expect(erro.or_(resultado_grid)).to_be_visible(timeout=30_000)

    existe = True
    if erro.is_visible():
        ctx.locator(".x-window-dlg button.x-btn-text", has_text="OK").click()
        existe = False

    # Fecha consulta
    clicar_com_ajax(ctx, ctx.locator("button[name='submitCancel']"))
    aguardar_ajax_global(page)

    return existe
