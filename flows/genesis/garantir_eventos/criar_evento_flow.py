from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.almoxarifado.gestao_de_compras.evento.navegar_para_evento_flow import (
    acessar_evento,
)
from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def criar_evento(page: Page, evento_data: dict[str, Any]) -> None:
    """Realiza o cadastro do evento abrangendo todo o ano vigente da competência."""
    nome_evento = evento_data["nome"]
    logger.info("Criando evento '{}'...", nome_evento)
    _preencher_formulario_evento(page, nome_evento)
    logger.info("Criação de evento concluída.")


def _preencher_formulario_evento(page: Page, nome: str) -> None:
    """Navega para a tela de evento e preenche as informações necessárias."""
    acessar_evento(page)

    ctx = escopo(page)

    ano = obter_data_almoxarifado(page, "DDMMYYYY")[-4:]
    dt_inicio = f"0101{ano}"
    dt_final = f"3112{ano}"

    page.mouse.move(0, 0)

    ctx.locator("input[name='dtInicio']").click()
    ctx.locator("input[name='dtInicio']").type(dt_inicio, delay=50)
    ctx.locator("input[name='dtFinal']").type(dt_final, delay=50)
    ctx.locator("input[name='dsPrevisaoCons']").type(nome)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
