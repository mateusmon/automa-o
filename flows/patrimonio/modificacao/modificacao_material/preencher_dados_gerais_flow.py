from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais(page: Page, bem: dict[str, str], bem_novo: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados gerais de modificação de material {}.", bem["nome"])

    ctx = escopo(page)
    nome_completo_bem = f"{bem['nome']} {bem['complemento']}"
    nome_completo_bem_novo = f"{bem_novo['nome']} {bem_novo['complemento']}"
    data = obter_data_patrimonio(page, formato="DD/MM/YYYY")

    preencher_campo(ctx, "input[name='bemServicoO']", nome_completo_bem)
    preencher_campo(ctx, "input[name='bemServicoD']", nome_completo_bem_novo)
    logger.info("Preenchendo campo de Data de Transferência com valor obtido da competência patrimonial '{}'.", data)
    ctx.locator("input[name='dtTransferencia']").fill(data)

    page.once("dialog", lambda dialog: dialog.accept())
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de modificação de material {}.", bem["nome"])
