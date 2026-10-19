
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def escolher_forma_operacao(page: Page, forma_operacao: str | None, fornecedor: dict[str, str]) -> None:
    """
    Seleciona a Forma de Operação por correspondência parcial
    (case-insensitive) e preenche os campos que aparecem em seguida (datas
    de aquisição/contabilização e agente). Se `forma_operacao` for
    None/vazio, mantém o valor padrão da interface.
    """
    logger.info("Iniciou escolha da Forma de Operação '{}'.", forma_operacao)

    ctx = escopo(page)
    _selecionar(ctx, page, forma_operacao)

    data_hoje = obter_data_patrimonio(page, "DD/MM/YYYY")

    data_recebimento_input = ctx.locator('input[name="dtAquisicao"]')
    data_recebimento_input.clear()
    logger.info("Preenchendo a data de recebimento com '{}'.", data_hoje)
    data_recebimento_input.fill(data_hoje)

    data_contabilizacao_input = ctx.locator('input[name="txDtContabil"]').or_(ctx.locator("input[name='dtContabil']"))
    aguardar_ajax_global(page)

    if data_contabilizacao_input.is_visible() and data_contabilizacao_input.is_enabled():
        data_contabilizacao_input.clear()
        logger.info("Preenchendo a data de contabilização com '{}'.", data_hoje)
        data_contabilizacao_input.fill(data_hoje)
        ctx.get_by_text("Data de Contabilização:").click()
        aguardar_ajax_global(page)
        # Precisa clicar fora do campo para a página atualizar
        ctx.get_by_text("Data de Contabilização:").click()

    aguardar_ajax_global(page)

    preencher_campo(ctx, 'input[name="agente"]', fornecedor["nome"])

    logger.info("Finalizou escolha da Forma de Operação '{}'.", forma_operacao)


def _selecionar(ctx, page: Page, forma_operacao: str | None) -> None:
    if not forma_operacao:
        logger.info("Forma de Operação padrão mantida.")
        return

    alvo = forma_operacao.upper().strip()
    select = ctx.locator("select[name='tipoBemFormaOperacao']")
    options = select.locator("option")

    for i in range(options.count()):
        option = options.nth(i)
        texto = option.inner_text().upper()

        if alvo in texto:
            select.select_option(value=option.get_attribute("value"))
            aguardar_ajax_global(page)
            logger.info("Forma de Operação selecionada: {}", texto)
            return

    raise ValueError(f"Forma de Operação não encontrada no select: {forma_operacao}")
