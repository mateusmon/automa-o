from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    preencher_campo,
)


def preencher_materiais(page: Page, material: dict, quantidade: str = "1") -> bool:
    logger.info("Iniciando preenchimento da aba 'Materiais' para o material '{}'.", material['nome'])

    ctx = escopo(page)

    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.get_by_role("button", name="Materiais").click()
    expect(ctx.get_by_role("heading", name="Totais")).to_be_visible()
    aguardar_ajax_global(page)

    # É necessário um número de Empenho para alguns tipos de entrada. 
    # Como ainda não foi criado um flow para cadastrar o Empenho. O teste lida como se fosse um erro esperado.
    select_tipo_movimento = ctx.locator("select[name='tipoMovimento']")
    if select_tipo_movimento.is_visible() and select_tipo_movimento.get_attribute("title") == "Não há itens. Clicar no botão 'Integração com Compras'.":
            logger.warning("Tipo de Entrada não utilizado.")
            return True

    if ctx.locator("input[name='precoMedioCkb']").is_checked():
        logger.info("Desmarcando 'Preço Médio' para o material '{}'.", nome_completo_material)
        ctx.locator("input[name='precoMedioCkb']").uncheck()

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, 'input[name="cdBemServico-1-3"]', nome_completo_material)

    quantidade_input = ctx.locator('input[name="qtNotaRecItem-2-5"]')
    quantidade_input.select_text()
    logger.info("Preenchendo quantidade do material: '{}'.", quantidade)
    quantidade_input.type(quantidade, delay=50)

    preco_unitario = float(material["preco_unitario"].replace(",", "."))
    preco_item = preco_unitario * int(quantidade)
    preco_formatado = f"{preco_item:.2f}".replace(".", ",")

    valor_input = ctx.locator('input[name="vlNotaRecItem-2-6"]')
    # para entrada tipo devolução ele não está habilitado
    if valor_input.is_enabled():
        logger.info("Preenchendo valor do material: '{}'.", preco_formatado)
        valor_input.clear()
        valor_input.type(preco_formatado, delay=50)

    valor_total_input = ctx.locator("#vlTotalInformado")
    texto_atual = valor_total_input.input_value().strip()

    if texto_atual:
        valor_existente = float(texto_atual.replace(".", "").replace(",", "."))
    else:
        valor_existente = 0.0

    novo_valor_total = valor_existente + preco_item

    valor_total_formatado = f"{novo_valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    logger.info("Preenchendo valor total informado: '{}'.", valor_total_formatado)
    valor_total_input.clear()
    valor_total_input.type(valor_total_formatado, delay=50)

    logger.info("Finalizando preenchimento da aba 'Materiais' para o material '{}'.", nome_completo_material)

    return False
