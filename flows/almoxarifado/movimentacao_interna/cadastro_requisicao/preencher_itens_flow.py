from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_itens(page: Page, material: dict, quantidade: str = "1") -> None:
    logger.info("Iniciou preenchimento de itens para o material '{}' com quantidade '{}'.", material["nome"], quantidade)

    ctx = escopo(page)
    _preencher(ctx, page, material, quantidade)

    logger.info("Finalizou preenchimento de itens para o material '{}' com quantidade '{}'.", material["nome"], quantidade)


def _preencher(ctx, page, material: dict[str, str], quantidade: str) -> None:
    linha = ctx.locator("table.tabela tbody[name='tboItens'] tr").first
    td = linha.locator("td")
    quantidade_td = td.count()

    logger.info("Preenchendo material '{}' com quantidade '{}'.", material["nome"], quantidade)
    preencher_campo(ctx, 'input[name="bemServico-1"]', f"{material['nome']} {material['complemento']}", lookup_name="lookup-bemServico-1-3")
    ctx.locator(f'input[name="qtRequisicao-2-{quantidade_td-3}"]').type(quantidade, delay=50)
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
