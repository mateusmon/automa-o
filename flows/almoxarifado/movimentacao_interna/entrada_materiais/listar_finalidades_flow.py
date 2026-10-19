from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def listar_finalidades(page: Page) -> list[str]:
    """
    Lista o texto de todas as finalidades disponíveis no <select> 'finalidade'
    do formulário de Entrada de Materiais.

    As finalidades disponíveis dependem do tipo de entrada selecionado, portanto
    esta função deve ser chamada APÓS `escolher_tipo_entrada`. Ignora a opção em
    branco/placeholder (sem value ou sem texto). Se o campo não existir ou não
    houver finalidades, retorna uma lista vazia.

    Parâmetros:
        page (Page): Instância da página do Playwright.

    Retorno:
        list[str]: Lista com os textos das finalidades disponíveis (pode ser vazia).
    """
    logger.info("Iniciou listagem das finalidades.")

    ctx = escopo(page)
    finalidades = _coletar_textos(ctx.locator('select[name="finalidade"]').locator("option"))

    logger.info("Finalizou listagem das finalidades. Total: {}.", len(finalidades))
    return finalidades


def _coletar_textos(options) -> list[str]:
    textos: list[str] = []
    for i in range(options.count()):
        option = options.nth(i)
        valor = (option.get_attribute("value") or "").strip()
        texto = option.inner_text().strip()
        if not valor or not texto:
            continue
        textos.append(texto)
        logger.info("Adicionando finalidade: '{}'", texto)
    return textos
