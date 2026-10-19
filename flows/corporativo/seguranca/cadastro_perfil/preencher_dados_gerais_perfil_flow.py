from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais_perfil(page: Page, perfil: dict) -> None:
    """
    Cadastra um Perfil MÍNIMO (Nome + Sistema + UMA funcionalidade/módulo) e confirma. É o
    único flow de preenchimento, então faz o submit (`submitFinish`) e aguarda o alerta.
    Cenário A.

    NÃO copia um perfil inteiro (o botão "Copiar perfil" traria TODAS as funcionalidades):
    monta um perfil enxuto com um único módulo, conforme o teste pede. Confirmado ao vivo que
    Nome + Sistema + 1 módulo basta para o Confirmar (não é preciso conceder permissão no lápis).

    Sistema (`sistema`) e Módulo (`contexto-1-3`) são lookups do tipo DIÁLOGO DE BUSCA (abre
    Consulta → filtra pelo Nome → Anexar a linha), não autocomplete — por isso são tratados
    explicitamente, e não via `preencher_campo`.

    :param perfil: dict do blueprint (`perfil_cr`): nome, sistema, modulo.
    """
    logger.info("Iniciou preenchimento de dados gerais de Perfil '{}'.", perfil["nome"])

    ctx = escopo(page)

    if ctx.locator("input[name='sistema']").is_disabled():
        ctx.locator("button[name='submitNew']").click()
        aguardar_ajax_global(page)
    logger.info("Preenchendo campo de Nome do Perfil com '{}'.", perfil["nome"])
    ctx.locator("input[name='nmPerfil']").fill(perfil["nome"])

    # Sistema — lookup diálogo: abre → filtra pelo Nome (model-0) → Anexar a linha.
    ctx.locator("button[name='lookup-sistema']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando Sistema pelo campo de Nome: '{}'.", perfil["sistema"])
    ctx.locator("input[name='model-0']").fill(perfil["sistema"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    ctx.locator(
        f"table[name='paginationTable'] tbody tr:has-text(\"{perfil['sistema']}\") button[name='submitUse']"
    ).click()
    aguardar_ajax_global(page)

    # Módulo (uma funcionalidade) — +linhas → lookup diálogo → filtra Nome (model-1) → Anexar.
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='lookup-contexto-1-3']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando Módulo pelo campo de Nome: '{}'.", perfil["modulo"])
    ctx.locator("input[name='model-1']").fill(perfil["modulo"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    ctx.locator(
        f"table[name='paginationTable'] tbody tr:has-text(\"{perfil['modulo']}\") button[name='submitUse']"
    ).click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Perfil '{}'.", perfil["nome"])
