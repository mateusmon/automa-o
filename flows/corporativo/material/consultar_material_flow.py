from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_material(page: Page, material: dict) -> None:
    """
    Dispara a busca de um material pelo complemento no form `bemser` (usado na exclusão
    de Consumo/Permanente/Serviço). Cenário A. Apenas prepara e abre a busca — a seleção
    do resultado fica no flow seguinte.

    O form não tem botão "Consulta" padrão: entra-se em Novo, preenche-se o complemento,
    clica-se fora (heading "Material") para disparar o ajax de validação e abre-se o
    lookup do complemento, que auto-filtra por COMPLEMENTO.

    :param material: dict do blueprint (usa a chave `complemento`).
    """
    logger.info("Iniciou consulta de material. '{}'.", material["complemento"])

    ctx = escopo(page)

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)
    logger.info("Preenchendo campo de Complemento do material com '{}'.", material["complemento"])
    ctx.locator("textarea[name='complemento_NmBemServico']").fill(material["complemento"])
    aguardar_ajax_global(page)

    # Clicar fora do campo (heading) dispara o ajax que valida o complemento
    ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='lookup-complemento_NmBemServico']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de material.'{}'.", material["complemento"])
