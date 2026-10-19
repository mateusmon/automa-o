from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def acoes_escolher_evento(page: Page, material: dict[str, str]) -> None:
    logger.info("Iniciou escolha de Evento para o material '{}'.", material["nome"])

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    linha = ctx.locator("table.tabela.material tbody tr").filter(
        has=ctx.locator(f"input[name^='cdBemServico'][value*='{nome_completo_material}']")
    ).first

    botao_acoes = linha.locator("button[name^='edit-cdBemServico']")
    botao_acoes.click()
    aguardar_ajax_global(page)

    campo_evento = ctx.locator("input[name='previsaoCons']")

    if not campo_evento.is_visible():
        ctx.locator('button[name="submitBack"]').click()
        aguardar_ajax_global(page)
        return

    logger.info("Preenchendo Evento: 'AUTOMATIZADO'.")
    preencher_campo(ctx, "input[name='previsaoCons']", "AUTOMATIZADO")

    ctx.locator('button[name="submitBack"]').click()
    aguardar_ajax_global(page)

    logger.info("Finalizou escolha de Evento.")
