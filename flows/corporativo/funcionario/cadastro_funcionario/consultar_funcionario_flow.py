from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_funcionario(page: Page, funcionario: dict) -> None:
    """
    Abre a Consulta de Funcionário e filtra por CPF (derivado da matrícula) (`model-4`, formatado).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param funcionario: dict do blueprint (usa a chave `matricula`).
    """
    logger.info("Iniciou consulta de Funcionário '{}'.", funcionario["matricula"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    _v = funcionario["matricula"]
    valor = f"{_v[:3]}.{_v[3:6]}.{_v[6:9]}-{_v[9:]}"
    logger.info("Filtrando consulta de Funcionário por CPF: '{}'.", valor)
    ctx.locator("input[name='model-4']").fill(valor)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Funcionário '{}'.", funcionario["matricula"])
