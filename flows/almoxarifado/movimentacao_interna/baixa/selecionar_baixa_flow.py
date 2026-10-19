from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_baixa(page: Page, material: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de baixa do material: '{}'.", material['nome'])

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    logger.info("Selecionando baixa do material: '{}'.", nome_completo_material)
    existe_baixa = selecionar_movimentacao(ctx, nome_completo_material)

    if not existe_baixa:
        logger.info("Não foi encontrado nenhuma baixa de material '{}'.", nome_completo_material)
        return False

    logger.info("Baixa do material '{}' selecionada com sucesso.", nome_completo_material)
    logger.info("Finalizou seleção de baixa do material: '{}'.", nome_completo_material)
    return True
