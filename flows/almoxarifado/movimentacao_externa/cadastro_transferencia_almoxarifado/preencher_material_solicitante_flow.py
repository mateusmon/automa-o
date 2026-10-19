from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_material_solicitante(
    page: Page,
    material: dict[str, str],
    quantidade: str = "1",
) -> None:
    logger.info("Iniciou preenchimento de material solicitante '{}'.", material["nome"])

    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx = escopo(page)
    _preencher_campos(ctx, nome_completo_material, quantidade)

    logger.info("Finalizou preenchimento de material solicitante '{}'.", material["nome"])


def _preencher_campos(ctx, nome_completo_material: str, quantidade: str) -> None:

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='cdBemServico-1-3']", nome_completo_material)

    logger.info("Preenchendo quantidade de requisição: '{}'.", quantidade)
    field_quantidade = ctx.locator("input[name='qtRequisicao-2-5']")
    field_quantidade.click()
    field_quantidade.fill(quantidade)
