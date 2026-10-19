from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, clicar_com_ajax


def alterar_material(page: Page) -> None:
    """
    Altera o Código Antigo (`cdMatAntigo`) do material no form `bemser` (compartilhado por
    Consumo/Permanente/Serviço) e confirma. Cenário A.

    O `cdMatAntigo` é um campo de texto livre, opcional e não-chave — recebe um valor fixo
    ("CR-ALT"), tornando a alteração idempotente e re-executável, sem afetar a Consulta
    (que filtra pelo complemento). O form `bemser` repopula os demais campos obrigatórios
    (subgrupo, U.M., conta, material genérico) ao Anexar, então basta confirmar.

    Pressupõe que o material já foi carregado (ver `selecionar_material`).
    """
    logger.info("Iniciou alteração de material.")

    ctx = escopo(page)
    logger.info("Alterando o Código Antigo do material para 'CR-ALT'.")
    ctx.locator("input[name='cdMatAntigo']").fill("CR-ALT")

    btn_confirmar = ctx.get_by_role("button", name="Confirmar")
    clicar_com_ajax(ctx, btn_confirmar)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de material.")
