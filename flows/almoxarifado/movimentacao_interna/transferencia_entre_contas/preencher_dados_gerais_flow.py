from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, material: dict[str, str], conta_contabil: str = "   ") -> None:
    logger.info("Iniciou preenchimento de dados gerais da transferência entre contas para o material '{}'.", material['nome'])

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='cdBemServico']", nome_completo_material)
    aguardar_ajax_global(page)

    # Preenche com a primeira conta disponível se nenhuma for informada
    logger.info("Preenchendo conta contábil: '{}'.", conta_contabil)
    preencher_campo(ctx, "input[name='contaNova']", conta_contabil)
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de dados gerais da transferência entre contas para o material '{}'.", material['nome'])
