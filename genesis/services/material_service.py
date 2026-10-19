from loguru import logger
from playwright.sync_api import Page, expect

from navigation.navegar_para_material import acessar_material
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def material_existe(page: Page, nome_material: str) -> bool:
    """
    Returns True if material exists, False otherwise.
    """
    resultado = True

    # Navigation
    if not acessar_material(page):
        logger.warning("Menu 'Material - Consumo' não disponível para este cliente. Ignorando verificação de material.")
        return False

    ctx = escopo(page)

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)

    # Search
    campo_bem = ctx.locator("textarea[name='complemento_NmBemServico']")
    campo_bem.fill(nome_material)
    aguardar_ajax_global(page)

    # Clicking out of the input field so that the page refreshes
    ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    # Click lookup and wait for the search panel to appear
    for tentativa in range(3):
        ctx.locator("button[name='lookup-complemento_NmBemServico']").click(no_wait_after=True)
        aguardar_ajax_global(page)
        try:
            ctx.locator("select[name='tpFil']").wait_for(state="visible", timeout=1_000)
            break
        except Exception:
            if tentativa == 2:
                raise RuntimeError("Painel de busca de bem não abriu após 3 tentativas.")
            aguardar_ajax_global(page)

    # If error panel related to COMPLEMENTO shows up, continue flow
    erro = ctx.locator(".ext-mb-text")
    resultado_grid = ctx.locator(".x-grid3-cell-inner.x-grid3-col-material").first
    expect(erro.or_(resultado_grid)).to_be_visible(timeout=30_000)
    if erro.is_visible():
        if "COMPLEMENTO" in erro.inner_text():
            ctx.locator(".x-window-dlg button.x-btn-text", has_text="OK").click()
            aguardar_ajax_global(page)
            ctx.locator(".ext-el-mask").wait_for(state="hidden")

    # Filter by bem
    ctx.select_option("select[name='tpFil']", value="tpFiltroMaterial")
    ctx.locator("button[name='lookup-filtro']").click()
    aguardar_ajax_global(page)

    # If error panel related to bem shows up, bem doesn't exist
    erro = ctx.locator(".ext-mb-text")
    resultado_grid = ctx.locator(".x-grid3-cell-inner.x-grid3-col-material").first
    expect(erro.or_(resultado_grid)).to_be_visible(timeout=30_000)

    if erro.is_visible():
        ctx.locator(".x-window-dlg button.x-btn-text", has_text="OK").click()
        resultado = False

    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)

    return resultado
