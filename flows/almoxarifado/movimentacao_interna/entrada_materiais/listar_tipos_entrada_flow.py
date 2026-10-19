from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def listar_tipos_entrada(page: Page) -> list[str]:
    """
    Lista o texto de todos os tipos de entrada disponíveis no <select>
    'tipoMovimento' do formulário de Entrada de Materiais.

    Ignora a opção em branco/placeholder (sem value ou sem texto). Os textos
    são retornados exatamente como exibidos na interface, prontos para serem
    repassados a `escolher_tipo_entrada`.

    Parâmetros:
        page (Page): Instância da página do Playwright.

    Retorno:
        list[str]: Lista com os textos dos tipos de entrada disponíveis.
    """
    logger.info("Iniciou listagem dos tipos de entrada.")

    ctx = escopo(page)
    tipos = _coletar_textos(ctx.locator('select[name="tipoMovimento"]').locator("option"))

    logger.info("Finalizou listagem dos tipos de entrada. Total: {}.", len(tipos))
    return tipos


def _coletar_textos(options) -> list[str]:
    textos: list[str] = []
    for i in range(options.count()):
        option = options.nth(i)
        valor = (option.get_attribute("value") or "").strip()
        texto = option.inner_text().strip()
        if not valor or not texto:
            continue
        textos.append(texto)
        logger.info("Adicionando tipo de entrada: '{}'", texto)
    return textos
