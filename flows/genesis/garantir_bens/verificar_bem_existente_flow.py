from typing import Any

from loguru import logger
from playwright.sync_api import Page, expect

from flows.corporativo.material.cadastro_material_permanente.navegar_para_material_permanente_flow import (
    acessar_material_permanente,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global


def verificar_bem_existente(
    page: Page, bens_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Mapeia os bens da massa e retorna os que ainda não estão cadastrados."""
    logger.info("Iniciando verificação de Bens existentes...")

    bens_faltantes = []
    total = len(bens_data)

    for indice, bem in enumerate(bens_data, start=1):
        logger.info("Verificando Bem {}/{}", indice, total)
        nome_bem = bem["nome"]
        complemento_bem = bem["complemento"]
        nome_completo = f"{nome_bem} {complemento_bem}"

        if _checar_existencia_bem_no_dom(page, nome_bem):
            logger.info("Bem '{}' já existe. Nenhuma ação necessária.", nome_completo)
        else:
            logger.info("Bem '{}' não encontrado. Marcado para criação.", nome_completo)
            bens_faltantes.append(bem)

    return bens_faltantes


def _checar_existencia_bem_no_dom(page: Page, nome_bem: str) -> bool:
    """Acessa a tela e verifica se o bem existe no sistema."""
    resultado = True

    acessar_material_permanente(page)

    ctx = escopo(page)

    ctx.locator("button[name='submitNew']").or_(
        ctx.get_by_role("button", name="Novo")
    ).first.wait_for(state="visible", timeout=15_000)

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)

    campo_bem = ctx.locator("textarea[name='complemento_NmBemServico']")
    campo_bem.fill(nome_bem)
    aguardar_ajax_global(page)

    if get_versao() >= 4:
        page.get_by_role("heading", name="Material - Permanente").click()
    else:
        page.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

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

    erro = ctx.locator(".ext-mb-text")
    resultado_grid = ctx.locator(".x-grid3-cell-inner.x-grid3-col-material").first
    expect(erro.or_(resultado_grid)).to_be_visible(timeout=30_000)

    if erro.is_visible() and "COMPLEMENTO" in erro.inner_text():
        ctx.locator(".x-window-dlg button.x-btn-text", has_text="OK").click()
        aguardar_ajax_global(page)
        ctx.locator(".ext-el-mask").wait_for(state="hidden")

    ctx.select_option("select[name='tpFil']", value="tpFiltroMaterial")
    ctx.locator("button[name='lookup-filtro']").click()
    aguardar_ajax_global(page)

    erro = ctx.locator(".ext-mb-text")
    resultado_grid = ctx.locator(".x-grid3-cell-inner.x-grid3-col-material").first
    expect(erro.or_(resultado_grid)).to_be_visible(timeout=30_000)

    if erro.is_visible():
        ctx.locator(".x-window-dlg button.x-btn-text", has_text="OK").click()
        resultado = False

    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)

    return resultado
