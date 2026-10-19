from loguru import logger
from playwright.sync_api import Page

from flows.almoxarifado.gestao_de_estoque.classificacao_material.shared.escolher_tipo_flow import escolher_tipo
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def escolher_natureza(page: Page, tipo: str) -> None:
    logger.info("Iniciou escolha de natureza de material.")

    ctx = escopo(page)

    logger.info("Escolhendo tipo de natureza de material '{}'.", tipo)
    escolher_tipo(page, "cdTpUsoEstoque", tipo)

    clicar_com_ajax(ctx, "button[name='submitAdicionar']")
    aguardar_ajax_global(page)
    clicar_com_ajax(ctx, "button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou escolha de natureza de material '{}'.", tipo)
