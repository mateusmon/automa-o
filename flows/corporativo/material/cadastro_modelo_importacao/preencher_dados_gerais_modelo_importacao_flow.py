from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais_modelo_importacao(page: Page, modelo: dict) -> None:
    """
    Preenche os dados gerais do Modelo de Importação: Descrição (`dsModelo`) e Material
    (`dsCompleta`, lookup). Cenário A (escopo via `escopo(page)`). Não consulta/seleciona
    característica nem confirma — o teste orquestra esses flows separadamente.

    O Material só aceita bens PERMANENTES no lookup — o dict do blueprint usa o bem
    provisionado por garantir_bens (ver `modelo_importacao_cr`).

    :param modelo: dict do blueprint (chaves `descricao` e `material`).
    """
    logger.info("Iniciou preenchimento de dados gerais de Modelo de Importação.")

    ctx = escopo(page)

    ctx.locator("input[name='dsModelo']").fill(modelo["descricao"])
    preencher_campo(ctx, "input[name='dsCompleta']", modelo["material"])

    logger.info("Finalizou preenchimento de dados gerais de Modelo de Importação.")
