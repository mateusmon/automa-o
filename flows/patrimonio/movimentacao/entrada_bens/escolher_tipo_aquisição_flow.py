import unicodedata

from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def escolher_tipo_aquisição(page: Page, tipo_entrada: str | None = None) -> None:
    """
    Seleciona o tipo de entrada no campo "Tipo de Entrada"
    com base em uma correspondência parcial do texto visível das opções.

    Estratégia:
        - Percorre dinamicamente todas as opções do <select>.
        - Seleciona a primeira opção cujo texto contenha o valor informado.
        - A comparação é case-insensitive.
        - Se nenhum tipo for informado, mantém o valor padrão da interface.

    Parâmetros:
        page (Page):
            Instância da página do Playwright.

        tipo_entrada (str | None):
            Texto parcial do tipo de entrada desejado.
            Exemplo:
                "extra"  -> seleciona "Compra extra-orçamentária"
                "doação" -> seleciona "Doação - Entrada"

            Se None ou vazio, o valor padrão (geralmente COMPRA)
            permanece selecionado.

    Exceções:
        ValueError:
            Caso o texto informado não corresponda a nenhuma opção disponível.
    """
    logger.info("Iniciou escolha do tipo de entrada '{}'.", tipo_entrada)

    ctx = escopo(page)
    _selecionar_tipo(ctx, page, tipo_entrada)

    logger.info("Finalizou escolha do tipo de entrada '{}'.", tipo_entrada)


def _normalizar_texto(texto: str) -> str:
    """Remove acentos e caracteres especiais para comparação flexível."""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()


def _selecionar_tipo(ctx, page: Page, tipo_entrada: str | None) -> None:
    if not tipo_entrada:
        logger.info("Tipo padrão mantido (COMPRA).")
        return

    select = ctx.locator('select[name="tipoBemFormaOperacao"]')
    expect(select).to_be_visible()
    select.locator("option").first.wait_for(state="attached", timeout=10000)
    alvo_normalizado = _normalizar_texto(tipo_entrada)
    options = select.locator("option")
    count = options.count()

    for i in range(count):
        option = options.nth(i)
        texto_bruto = option.inner_text()
        texto_normalizado = _normalizar_texto(texto_bruto)

        if alvo_normalizado in texto_normalizado:
            value = option.get_attribute("value")
            select.select_option(value=value)
            select.dispatch_event("change")
            aguardar_ajax_global(page)
            logger.info(f"Tipo de entrada selecionado com sucesso: {texto_bruto.strip()}")
            return

    raise ValueError(f"Tipo de entrada '{tipo_entrada}' não foi encontrado entre as {count} opções disponíveis no <select>.")
