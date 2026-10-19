from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def excluir_enderecamento_material(page: Page, endereco: str) -> str:
    logger.info("Excluindo endereçamento de material para o endereço '{}'.", endereco)

    ctx = escopo(page)

    linhas = ctx.locator("table.tabela tbody[name='tboItens'] tr")
    quantidade = linhas.count()

    for i in range(quantidade):
        ordem = i + 1
        valor_endereco = ctx.locator(f"input[name='endereco-{ordem}-3']").input_value()

        if endereco.lower() not in valor_endereco.lower():
            continue

        ctx.locator(f"input[name='deletable-{ordem}-1']").check()

        clicar_com_ajax(ctx, "button[name='submitFinish']")
        aguardar_ajax_global(page)
        try:
            esperar_sucesso_ou_erro(ctx)
        except RuntimeError as e:
            mensagem_erro = str(e).lower()
            termos_skip = ["saldo"]
            if any(termo in mensagem_erro for termo in termos_skip):
                return False
            raise
        
        logger.info("Endereçamento de Material excluído para o endereço '{}'.", endereco)

        return valor_endereco

    raise RuntimeError(f"Endereço '{endereco}' não encontrado na tabela de endereçamento.")