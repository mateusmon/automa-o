from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, select_tipo

def selecionar_situacao(page: Page, desfazer: bool, situcao_fisica: str = "") -> str:
    logger.info("Iniciando seleção de situação física.")

    ctx = escopo(page)

    situacao_anterior = ctx.locator("input[name='bens-2-6']").input_value()

    if desfazer:
        select_tipo(ctx, "bens-2-7", situcao_fisica)
    else:
        # Os códigos de situação física variam por cliente (ex.: JFRJ não tem
        # o código "01"), então escolhe a primeira opção disponível diferente
        # da situação atual, em vez de um código fixo.
        select = ctx.locator("select[name='bens-2-7']")
        nova_situacao = select.evaluate(
            """(select, atual) => {
                const option = Array.from(select.options).find(
                    o => o.value && o.text.trim() !== atual
                );
                return option ? option.value : null;
            }""",
            situacao_anterior
        )

        if nova_situacao is None:
            raise RuntimeError("Nenhuma outra situação física disponível para seleção.")

        select.select_option(value=nova_situacao)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Situação física selecionada com sucesso.")
    return situacao_anterior