from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_supply(page: Page, supply: dict) -> None:
    """
    Cadastra um Grupo → Subgrupo → Material inteiramente NOVOS no Supply, por texto livre,
    e confirma. Cenário A. É o único flow de preenchimento, portanto faz o submit
    (`submitFinish`) e aguarda o alerta de sucesso/erro.

    Sequência: digita o Grupo (código+nome) → "+ Subgrupos" (`submitAddLine1`) habilita os
    campos do Subgrupo → digita o Subgrupo (código+nome) → "+ Materiais" (`submitAddLine2`)
    habilita os do Material → digita o nome do Material (o código é gerado pelo sistema).

    Os dados são inventados e autocontidos (grupo 100 é alto/livre, fora do intervalo SIASG
    00–99), garantindo unicidade em qualquer cliente para o par Cadastro+Exclusão.

    :param supply: dict do blueprint (grupo_codigo, grupo_nome, subgrupo_codigo,
        subgrupo_nome, material_nome).
    """
    logger.info("Iniciou preenchimento de Supply.")

    ctx = escopo(page)

    ctx.locator("input[name='grupoCdExemplo']").fill(supply["grupo_codigo"])
    ctx.locator("input[name='grupoDsExemplo']").fill(supply["grupo_nome"])

    ctx.locator("button[name='submitAddLine1']").click()  # + Subgrupos
    aguardar_ajax_global(page)
    ctx.locator("input[name='subgrupoCdExemplo']").fill(supply["subgrupo_codigo"])
    ctx.locator("input[name='subgrupoDsExemplo']").fill(supply["subgrupo_nome"])

    ctx.locator("button[name='submitAddLine2']").click()  # + Materiais
    aguardar_ajax_global(page)
    ctx.locator("input[name='materialDsExemplo']").fill(supply["material_nome"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de Supply.")
