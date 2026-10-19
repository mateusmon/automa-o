from loguru import logger
from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def selecionar_ur_material(page: Page) -> None:
    logger.info("Iniciou a seleção da UR para o material.")

    ctx = escopo(page)

    # 1. Clica no botão 'Editar' da primeira linha do material
    logger.info("Abrindo edição da primeira linha do material.")
    btn_editar_material = ctx.locator("button.btnEditar[rowid='2']")
    expect(btn_editar_material).to_be_visible()
    clicar_com_ajax(ctx, btn_editar_material)

    # 2. Inicio da busca pela UR a ser selecionada
    logger.info("Abrindo consulta avançada de UR.")

    input_ur = ctx.locator("input[name='ur']")

    try:
        # Define um timeout curto (3000ms) para não esperar os 60s padrão
        if input_ur.is_visible(timeout=3000):
            preencher_campo(ctx, input_ur, "   ")
        else:
            logger.warning(
                "Campo 'input[name=ur]' não está visível. Pulando etapa."
            )

    except PlaywrightTimeoutError:
        logger.warning(
            "Timeout excedido ao procurar o campo de UR Prosseguindo."
        )
    except Exception as e:
        logger.warning(
            f"Não foi possível preencher a UR: {e}. Prosseguindo."
        )

    finally:
        # 5. Clica no botão Retornar para fechar o formulário
        logger.info("Retornando ao formulário principal de materiais.")
        btn_retornar = ctx.locator("button[name='submitBack'], button[title='Retornar']:has-text('Retornar')").first
        expect(btn_retornar).to_be_visible()
        clicar_com_ajax(ctx, btn_retornar)

    logger.info("Finalizou a seleção da UR para o material.")
