# Por enquanto este flow garante somente a criação de subgrupos.
# Ainda não encontramos um cliente que precise da criação de grupos e subgrupos.
# Ele é um flow reserva.

from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_subgrupo import acessar_subgrupo
from services.subgrupo_service import subgrupo_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo


def garantir_subgrupos(context: ExecutionContext) -> None:
    """
    Ensures subgrupos exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    grupos_data = blueprint.get("grupos")

    if not grupos_data:
        logger.info("Nenhum grupo ou subgrupo definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_subgrupo(page):
        logger.warning("Menu 'Supply' não disponível para este cliente. Pulando fluxo de subgrupos.")
        return
    
    total = len(grupos_data)

    logger.info("Foi encontrado um total de {} grupos no arquivo yaml.", total)

    for atual, grupo in enumerate(grupos_data, start=1):
        logger.info("Grupo {}/{}", atual, total)

        nome_grupo = grupo["nome"]
        logger.info("Garantindo subgrupos para o grupo nome '{}'", nome_grupo)
        
        subgrupos = grupo["subgrupos"]
        total_subgrupos = len(subgrupos)
        algum_criado = False

        for indice_subgrupo, subgrupo in enumerate(subgrupos, start=1):
            logger.info("Subgrupo {}/{}", indice_subgrupo, total_subgrupos)
            
            if subgrupo_existe(page, subgrupo["codigo"]):
                logger.info("Subgrupo com nome '{}' já existe. Nenhuma ação necesária.", subgrupo["nome"])
                continue

            logger.info("Subgrupo com nome '{}' não encontrado. Criando...", subgrupo["nome"])
            _criar_subgrupo(page, subgrupo)

            if not subgrupo_existe(page, subgrupo["codigo"]):
                raise RuntimeError(
                    f"Falha ao validar criação de subgrupo '{subgrupo['nome']}'."
                )

            logger.success("Subgrupo '{}' criado com sucesso.", subgrupo["nome"])
            algum_criado = True

        if algum_criado:
            logger.success("Subgrupos do grupo '{}' criados com sucesso.", nome_grupo)


def _criar_subgrupo(page: Page, subgrupo_data: dict) -> None:
    """
    Performs deterministic creation of subgrupo.
    Assumes prior existence check returned False.
    """
    codigo_subgrupo = subgrupo_data["codigo"]
    nome_subgrupo = subgrupo_data["nome"]

    if not acessar_subgrupo(page):
        logger.warning("Menu 'Supply' não disponível para este cliente. Impossível criar subgrupo.")
        return

    ctx = escopo(page)

    ctx.locator("button[name='lookup-grupoDsExemplo']").click()
    aguardar_ajax_global(page)
    
    preencher_campo(ctx, "input[name='filtro']", codigo_subgrupo[:2])

    ctx.locator("img.x-tree-node-icon.icon-grupo-open").dblclick()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitAddLine2']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='subgrupoCdExemplo']").fill(codigo_subgrupo)
    ctx.locator("input[name='subgrupoDsExemplo']").fill(nome_subgrupo)
    ctx.locator("input[name='materialDsExemplo']").fill("MATERIAL AUTOMATIZADO")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
