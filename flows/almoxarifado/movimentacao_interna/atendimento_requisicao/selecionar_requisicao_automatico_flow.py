from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_requisicao_automatico(page: Page, ur: dict[str, str]) -> bool:
    """
    Seleciona para atendimento a última requisição da UR e depois clica no botão "Automático".
    Retorna False se nenhuma requisição for encontrada ou se houver erro ao salvar.
    """
    logger.info("Iniciou seleção e atendimento automático de requisição na UR '{}'.", ur["nome"])

    ctx = escopo(page)
    result = _selecionar_e_submeter(ctx, page, ur)

    if result:
        logger.info("Finalizou seleção e atendimento automático de requisição na UR '{}'.", ur["nome"])

    return result


def _selecionar_e_submeter(ctx, page: Page, ur: dict[str, str]) -> bool:
    logger.info("Iniciou consulta de atendimento de requisição na UR '{}'.", ur["nome"])

    if not _localizar_e_marcar_requisicao(ctx, ur):
        return False

    ctx.locator("button[name='submitAutomatico']").click()
    aguardar_ajax_global(page)

    mensagem_erro = ctx.get_by_text("O formulário contém erros.")
    if mensagem_erro.is_visible():
        titulo = ctx.locator("input[name='qtAtendido-1-1-13']").get_attribute("title")
        logger.error("Erro gerado: {}", titulo)
        return False

    logger.info("Finalizou atendimento automático de requisição na UR '{}'.", ur["nome"])
    return True


def _localizar_e_marcar_requisicao(ctx, ur: dict[str, str]) -> bool:
    logger.info("Iniciou localização e marcação de requisição na UR '{}'.", ur["nome"])

    linhas = ctx.locator("table.tabelaComRolagem tbody tr")
    total = linhas.count()

    for i in range(total - 1, -1, -1):
        linha = linhas.nth(i)

        ur_linha = linha.locator("td").nth(4).text_content()
        ur_linha = ur_linha.strip() if ur_linha else ""
        ur_linha = ur_linha.split(" - ", 1)[1] if " - " in ur_linha else ur_linha

        if ur_linha in ur["nome"]:
            logger.debug("Requisição encontrada para a UR {} na linha {}.", ur["nome"], i)
            linha.locator("td").nth(8).locator("input[type='checkbox']").check()
            return True

    logger.info("Nenhuma requisição foi encontrada para a UR {}.", ur["nome"])
    return False
