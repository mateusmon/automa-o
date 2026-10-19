from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo
from flows.patrimonio.modificacao.alteracao_individual_bem.consultar_bem_flow import consultar_bem


def preencher_dados_gerais(page: Page, ug: dict[str, str], bem: dict[str, str], valor_requisicao: str = "753,52") -> bool:
    logger.info("Iniciou preenchimento de dados gerais do bem '{}'.", bem["nome"])

    ctx = escopo(page)
    nome_completo_bem = f"{bem['nome']} {bem['complemento']}"

    preencher_campo(ctx, "input[name='ugUl']", ug["codigo"])

    ctx.locator("button[name='lookup-bem']").click()
    aguardar_ajax_global(page)

    bem_existe = consultar_bem(page, ug, bem)

    if not bem_existe:
        logger.info("Nenhum bem encontrado para o material '{}'.", nome_completo_bem)
        return False

    if ctx.locator("input[name='vlUnitario']").is_enabled():
        logger.info("Preenchendo campo de Valor Unitário com '{}'.", valor_requisicao)
        ctx.locator("input[name='vlUnitario']").fill(valor_requisicao)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais do bem '{}'.", bem["nome"])
    return True
