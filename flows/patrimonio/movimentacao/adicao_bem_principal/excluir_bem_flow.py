from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def excluir_bem(page: Page, bem_adicionado: dict[str, str]) -> None:
    nome_completo_bem = f"{bem_adicionado['nome']} {bem_adicionado['complemento']}"

    logger.info("Iniciou exclusão do bem adicionado '{}'.", nome_completo_bem)

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitRestore']"))

    linha = (
        ctx.locator("table.tabelaComRolagem tbody tr")
        .filter(has_text=nome_completo_bem)
        .first
    )

    linha.locator("input[type='checkbox']").click()

    campo_patrimonio = linha.locator("input[name^='cdBemPerm']")
    campo_data = linha.locator("input[name^='dtHistorico']")

    if campo_patrimonio.input_value().strip() and campo_data.is_enabled():
        data = obter_data_patrimonio(ctx, formato="DD/MM/YYYY")
        campo_data.fill(data)

    aguardar_ajax_global(page)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitConfirm']"))
    esperar_sucesso_ou_erro(ctx)

    logger.info("Bem '{}' excluído.", nome_completo_bem)
