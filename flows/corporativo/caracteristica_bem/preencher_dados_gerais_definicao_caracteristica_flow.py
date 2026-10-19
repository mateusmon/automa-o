from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais_definicao_caracteristica(page: Page, caracteristica: dict) -> None:
    """
    Preenche a Definição da Característica do Bem e confirma. É o único flow de preenchimento,
    portanto faz o submit (`submitFinish`) e aguarda o alerta de sucesso/erro. Cenário A.

    Campos: Nome (`nmCaracteristica`), Tamanho (`nrTamanho`) e Tabelado (radio `inTabelado`).
    Tipo de dado (`tipoDado` = CARACTERE), Máscara (`dsMascara` = C*) e Unicidade
    (`cdTpUnicidade` = Nenhum) ficam nos padrões do form. O Código é gerado pelo sistema.
    Marcar Tabelado = Sim não abre seção obrigatória de valores (confirmado ao vivo).

    :param caracteristica: dict do blueprint (`caracteristica_bem_cr`): nome, tamanho, tabelado.
    """

    logger.info("Iniciou preenchimento de dados gerais da Definição da Característica '{}'.", caracteristica["nome"])

    ctx = escopo(page)

    logger.info("Preenchendo Nome da Definição da Característica: '{}'.", caracteristica["nome"])
    ctx.locator("input[name='nmCaracteristica']").fill(caracteristica["nome"])
    logger.info("Preenchendo Tamanho da Definição da Característica: '{}'.", caracteristica["tamanho"])
    ctx.locator("input[name='nrTamanho']").fill(caracteristica["tamanho"])

    tabelado = "S" if str(caracteristica.get("tabelado", "")).strip().lower() in ("sim", "s") else "N"
    ctx.locator(f"input[name='inTabelado'][value='{tabelado}']").check()

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais da Definição da Característica '{}'.", caracteristica["nome"])
