from decimal import Decimal

from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def editar_materiais(page: Page, material: dict[str, str]) -> bool:
    logger.info("Iniciou a edição de materiais para o material '{}'.", material["nome"])

    ctx = escopo(page)

    ctx.get_by_role("button", name="Materiais").click()
    expect(ctx.get_by_role("heading", name="Totais")).to_be_visible()
    aguardar_ajax_global(page)

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    campo_material = ctx.locator('input[name="cdBemServico-1-3"]')
    campo_material.wait_for(state="visible")
    valor_campo = campo_material.input_value()
    quantidade_atual = ctx.locator("input[name='qtNotaRecItem-1-5']").input_value()

    if nome_completo_material.lower() not in valor_campo.lower():
        raise ValueError(
            f"Material esperado '{nome_completo_material}' não encontrado no campo."
        )

    preco_unitario = material["preco_unitario"]

    if quantidade_atual == "1":
        nova_quantidade = "2"
        novo_valor = str(Decimal(preco_unitario.replace(",", ".")) * 2).replace(
            ".", ","
        )
    elif quantidade_atual == "2":
        nova_quantidade = "1"
        novo_valor = preco_unitario
    else:
        raise ValueError(f"Quantidade atual inesperada: '{quantidade_atual}'.")

    logger.info(
        "Alterando quantidade: '{}' -> '{}'.", quantidade_atual, nova_quantidade
    )
    ctx.locator("#qtNotaRecItem").dblclick()
    ctx.locator("#qtNotaRecItem").fill(nova_quantidade)

    logger.info("Alterando valor unitário: '{}' -> '{}'.", preco_unitario, novo_valor)
    ctx.locator("#valorItem").dblclick()
    ctx.locator("#valorItem").fill(novo_valor)

    ctx.locator("#vlTotalInformado").dblclick()

    valor_acumulado = ctx.locator("input[name='vlSomatorio']").input_value()

    logger.info(
        "Alterando valor total informado: '{}' -> '{}'.",
        ctx.locator("#vlTotalInformado").input_value(),
        valor_acumulado,
    )
    ctx.locator("#vlTotalInformado").fill(valor_acumulado)

    checkbox = ctx.locator('input[name="precoMedioCkb"]')

    if checkbox.is_checked():
        logger.info("Desmarcando o checkbox de preço médio.")
        checkbox.uncheck()
        aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    try:
        esperar_sucesso_ou_erro(ctx)
    except RuntimeError as e:
        mensagem_erro = str(e).lower()
        termos_skip = ["movimentação posterior"]
        if any(termo in mensagem_erro for termo in termos_skip):
            return False
        raise

    expect(ctx.get_by_text("Entrada alterada com sucesso!")).to_be_visible()

    logger.info(
        "Finalizou a edição de materiais para o material '{}'.", material["nome"]
    )
    return True
