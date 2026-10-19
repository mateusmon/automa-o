from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_evento import acessar_evento
from services.evento_service import evento_existe
from utils.competencia_financeira import obter_data_almoxarifado
from utils.espera import aguardar_ajax_global, esperar_sucesso_ou_erro
from utils.versao_gen import escopo


def garantir_evento(context: ExecutionContext) -> None:
    """
    Ensures the evento exists according to blueprint, spanning the whole year.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    evento_data = blueprint.get("evento")

    if not evento_data:
        logger.info("Nenhum evento definido no arquivo yaml. Ignorando fluxo.")
        return

    nome_evento = evento_data["nome"]

    if not acessar_evento(page):
        logger.error("Menu 'Evento' não disponível para este cliente.")
        return

    logger.info("Garantindo evento '{}'", nome_evento)

    if evento_existe(page, nome_evento):
        logger.info("Evento '{}' já existe. Nenhuma ação necesária.", nome_evento)
        return

    logger.info("Evento '{}' não encontrado. Criando...", nome_evento)

    _criar_evento(page, nome_evento)

    # --- Post-creation validation ---
    if not evento_existe(page, nome_evento):
        raise RuntimeError(f"Falha ao validar criação de evento '{nome_evento}'.")

    logger.success("Evento '{}' criado com sucesso.", nome_evento)


def _criar_evento(page: Page, nome: str) -> None:
    """
    Performs deterministic creation of evento, covering the entire year (01/01 a 31/12).
    Assumes prior existence check returned False.
    """

    # Navigation
    if not acessar_evento(page):
        logger.error("Menu 'Evento' não disponível para este cliente.")
        return

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