from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_itens_completo(page: Page, material: dict, quantidade: str = "1") -> None:
    logger.info("Iniciou preenchimento de itens completo para o material '{}' com quantidade '{}'.", material["nome"], quantidade)

    ctx = escopo(page)
    _preencher(ctx, material, quantidade)

    logger.info("Finalizou preenchimento de itens completo para o material '{}' com quantidade '{}'.", material["nome"], quantidade)


def _preencher(ctx, material: dict[str, str], quantidade: str) -> None:
    linha = ctx.locator("table.tabela tbody[name='tboItens'] tr").first
    td = linha.locator("td")
    quantidade_td = td.count()

    logger.info("Preenchendo material '{}' com quantidade '{}'.", f"{material['nome']} {material['complemento']}", quantidade)
    preencher_campo(ctx, 'input[name="bemServico-1"]', f"{material['nome']} {material['complemento']}",lookup_name="lookup-bemServico-1-3")
    ctx.locator(f'input[name="qtRequisicao-2-{quantidade_td-3}"]').type(quantidade, delay=50)