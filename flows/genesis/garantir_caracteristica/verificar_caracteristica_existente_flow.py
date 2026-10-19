from loguru import logger
from playwright.sync_api import Page

from flows.corporativo.material.cadastro_material_permanente.navegar_para_material_permanente_flow import (
    acessar_material_permanente,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_caracteristica_existente(page: Page) -> bool:
    """Acessa a tela do Bem e verifica se o campo de característica possui algum valor preenchido."""
    logger.info("Verificando relacionamento de característica com o Bem...")
    return _checar_caracteristica_no_dom(page)


def _checar_caracteristica_no_dom(page: Page) -> bool:
    """Acessa o formulário do bem e retorna True caso já tenha uma característica vinculada."""
    acessar_material_permanente(page)

    ctx = escopo(page)

    campo_bem = ctx.locator('textarea[name="complemento_NmBemServico"]')
    campo_bem.clear()
    campo_bem.fill("M01 MESA")
    aguardar_ajax_global(page)

    ctx.locator('button[name="lookup-complemento_NmBemServico"]').click()
    aguardar_ajax_global(page)

    ctx.locator('img[title="Retornar"]').click()
    aguardar_ajax_global(page)

    ctx.locator('button[name="submitTabCaracteristicas"]').click()
    aguardar_ajax_global(page)

    valor = ctx.locator('input[name="caracteristicas-Nome-1-3"]').input_value()
    logger.info("Valor da característica encontrada: '{}'", valor)

    return valor.strip() != ""
