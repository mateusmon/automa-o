from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_transferencia(page: Page, material: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de transferência entre contas para o material '{}'.", material['nome'])
    ctx = escopo(page)

    nome_completo_material = f"{material['nome']} {material['complemento']}"

    existe_movimentacao = selecionar_movimentacao(ctx, nome_completo_material)

    if not existe_movimentacao:
        logger.info("Não foi encontrada nenhuma transferência entre contas para o material '{}'.", nome_completo_material)
    else:
        logger.info("Foi encontrada uma transferência entre contas para o material '{}'.", nome_completo_material)

    logger.info("Finalizou seleção de transferência entre contas para o material '{}'.", material['nome'])
    return existe_movimentacao
