from playwright.sync_api import Page, expect
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def selecionar_materiais(page: Page) -> None:
    logger.info("Iniciou seleção de materiais para catálogo restrito.")

    ctx = escopo(page)

    # Indo para página de consulta
    ctx.locator("button[name='lookup-bemServOrgao-1-3']").click()
    aguardar_ajax_global(page)
    expect(page.get_by_role("heading", name="Consultar Material").or_(page.get_by_role("heading", name="Auxiliares - Catálogo Restrito"))).to_be_visible()

    # Pesquisando todos os materiais que têm "AUTOMATIZADO" no nome
    ctx.locator("input[name='model-4']").type("AUTOMATIZADO", delay=50)
    preencher_campo(ctx, "input[name='model-9']", "UMT")
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)
    expect(page.get_by_text("Material - Resultado da").or_(page.get_by_role("heading", name="Auxiliares - Catálogo Restrito"))).to_be_visible()

    # Adicionando todos os materiais
    ctx.get_by_role("button", name="Adicionar todos").click()
    aguardar_ajax_global(page)

    # Carregando todos os materiais
    ctx.locator("button[name='submitUseSelected']").click()
    aguardar_ajax_global(page)
    expect(page.get_by_role("heading", name="Catálogo de material").or_(page.get_by_role("heading", name="Auxiliares - Catálogo Restrito"))).to_be_visible()
    
    logger.info("Finalizou seleção de materiais para catálogo restrito.")

    # Confirmando
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
