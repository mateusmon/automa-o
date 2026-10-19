from decimal import Decimal
from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_multiplos_materiais(
    page: Page,
    bens: list[dict[str, str]],
    quantidade: str = "1",
) -> None:
    """
    Preenche múltiplos bens na aba 'Materiais' da Entrada de Bens do Patrimônio.
    Otimizado para preencher exclusivamente os campos estritamente necessários,
    minimizando o tempo total de execução do teste:

    - Preenche apenas o bem (lookup obrigatório).
    - Evita redigitar quantidade se o campo já contiver o valor desejado.
    - Preenche o valor unitário da linha apenas se necessário.
    - Preenche o valor total consolidado (vlTotalNF) uma única vez ao final.
    - Pula abas e campos opcionais.
    """
    logger.info("Iniciou preenchimento de múltiplos materiais na Entrada de Bens. Total de itens: {}", len(bens))

    ctx = escopo(page)
    _preencher(ctx, page, bens, quantidade)

    logger.info("Finalizou preenchimento de múltiplos materiais na Entrada de Bens .")


def _preencher(ctx, page: Page, bens: list[dict[str, str]], quantidade: str) -> None:
    ctx.get_by_role("button", name="Materiais").click()
    aguardar_ajax_global(page)

    total_geral = Decimal("0.00")
    qtd_int = int(quantidade)

    for i, bem in enumerate(bens, start=1):
        nome_bem = bem["nome"]
        complemento_bem = bem["complemento"]
        nome_completo_bem = f"{nome_bem} {complemento_bem}"
        preco_unitario_str = str(bem.get("preco_unitario", "0,00")).replace(",", ".")
        preco_unitario_dec = Decimal(preco_unitario_str)

        logger.info("Preenchendo bem {}/{}: {}", i, len(bens), nome_completo_bem)

        # Adiciona nova linha a partir do segundo item caso ainda não esteja visível
        if i > 1:
            campo_bem_atual = ctx.locator(f'input[name="bemServOrgao-{i}-3"]')
            if not campo_bem_atual.is_visible():
                botao_add = ctx.locator("button[name='submitAddLine1'], button[name='submitAddLine'], button[name='submitAddLine2']")
                if botao_add.is_visible() and botao_add.is_enabled():
                    botao_add.first.click()
                    aguardar_ajax_global(page)

        # 1. Campo do Bem (Obrigatório)
        seletor_bem = f'input[name="bemServOrgao-{i}-3"]'
        if not ctx.locator(seletor_bem).is_visible():
            seletor_bem = f'input[name^="bemServOrgao-{i}-"]'

        preencher_campo(ctx, seletor_bem, nome_completo_bem)

        # 2. Quantidade (Só digita se o valor atual for diferente para evitar atraso)
        seletor_qtd = f'input[name="quantidade-{i}-4"]'
        if not ctx.locator(seletor_qtd).is_visible():
            seletor_qtd = f'input[name^="quantidade-{i}-"]'

        quantidade_input = ctx.locator(seletor_qtd)
        if quantidade_input.is_visible() and quantidade_input.input_value().strip() != quantidade:
            quantidade_input.select_text()
            quantidade_input.fill(quantidade)

        # 3. Cálculo do valor unitário e acumulação do total
        subtotal_item = preco_unitario_dec * qtd_int
        total_geral += subtotal_item
        preco_formatado = f"{preco_unitario_dec:.2f}".replace(".", ",")

        # 4. Valor do Item (Preenche de forma ágil)
        seletor_valor = f'input[name="valor-{i}-6"]'
        if not ctx.locator(seletor_valor).is_visible():
            seletor_valor = f'input[name^="valor-{i}-"]'

        valor_input = ctx.locator(seletor_valor)
        if valor_input.is_visible() and valor_input.input_value().strip() != preco_formatado:
            valor_input.clear()
            valor_input.fill(preco_formatado)

    # 5. Valor Total da NF (Preenchido uma única vez ao final)
    total_formatado = f"{total_geral:.2f}".replace(".", ",")
    logger.info("Preenchendo valor total da NF: R$ {}", total_formatado)
    valor_total_input = ctx.locator('input[name="vlTotalNF"]')
    valor_total_input.clear()
    logger.info("Limpando campo de valor total da NF.")
    valor_total_input.fill(total_formatado)
