from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_material(page: Page, material: dict) -> bool:
    """
    Trata o resultado da busca do material (form `bemser`, exclusão de
    Consumo/Permanente/Serviço) e carrega o registro no formulário. Cenário A.
    Pressupõe que a consulta já foi disparada (ver `consultar_material`).

    O painel pode retornar duas coisas:
      - uma linha com o material → clica-se no ícone "Retornar" para carregá-lo (True);
      - o alerta "Nenhum COMPLEMENTO encontrado!" (quando o material não existe) →
        dispensa-se o alerta, cancela-se a busca e retorna-se False (nada a excluir).

    :param material: dict do blueprint (usa a chave `complemento`, só para log).
    :return: True se o material foi encontrado e carregado; False caso contrário.
    """
    logger.info("Iniciou seleção de material '{}'.", material["complemento"])

    ctx = escopo(page)

    # A busca retorna a linha do material OU o alerta de "não encontrado"
    alerta = ctx.locator(".ext-mb-text").first
    linha = ctx.locator(".x-grid3-body .x-grid3-row").first
    expect(alerta.or_(linha)).to_be_visible(timeout=30_000)

    if alerta.is_visible():
        logger.info("Nenhum material encontrado para '{}'.", material["complemento"])
        ctx.locator(".x-window-dlg button:has-text('OK')").click()
        aguardar_ajax_global(page)
        ctx.locator(".ext-el-mask").first.wait_for(state="hidden")
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    # Ícone "Retornar" da linha carrega o material no formulário
    linha.locator("img[title='Retornar']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de material '{}'.", material["complemento"])
    return True
