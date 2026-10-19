from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, material: dict[str, str]) -> None:
    logger.info(
        "Iniciou preenchimento de dados gerais para o material '{}'.", material["nome"]
    )

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='bemServOrgao']", nome_completo_material)

    logger.info(
        "Finalizou preenchimento de dados gerais para o material '{}'.",
        material["nome"],
    )
