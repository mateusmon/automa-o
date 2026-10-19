from loguru import logger
from playwright.sync_api import Page

from utils.erros_input import logar_erros_de_campos
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def excluir_movimento(page: Page, esperar_sucesso: bool = False) -> bool:
    """
    Este flow pode ser usado em todos testes de exclusão de todos os módulos.
    O "esperar_sucesso" só deve ser True quando estiver realizando uma exclusão
    no Almoxarifado (que exibe mensagem Toast de sucesso).
    """
    logger.info("Iniciou exclusão de cadastro.")

    ctx = escopo(page)
    resultado = _excluir(ctx, page, esperar_sucesso)

    logger.info("Finalizou exclusão de cadastro.")
    return resultado


def _excluir(ctx, page: Page, esperar_sucesso: bool) -> bool:
    btn_excluir = ctx.get_by_role("button", name="Excluir")

    if btn_excluir.count() == 0 or btn_excluir.is_disabled():
        logger.info("Botão de exclusão indisponível ou desabilitado.")
        return False

    page.once("dialog", _aceitar_confirmacao)
    clicar_com_ajax(ctx, btn_excluir)
    aguardar_ajax_global(page)

    # 1. Se o sistema exibiu erro de validação/bloqueio, captura a mensagem real do ASI
    erro = ctx.locator(".alert-danger")
    if erro.count() > 0 and erro.first.is_visible():
        erros_campos = logar_erros_de_campos(ctx)
        msg_alerta = erro.first.inner_text().strip()
        detalhes = f"{msg_alerta} | Detalhes: {'; '.join(erros_campos)}" if erros_campos else msg_alerta
        mensagem_erro = detalhes.lower()
        termos_skip = ["movimentação", "bloqueada", "superior"]
        if any(termo in mensagem_erro for termo in termos_skip):
            logger.warning("Exclusão não permitida: {}", detalhes)
            return False
        raise RuntimeError(f"Erro na exclusão: {detalhes}")

    if esperar_sucesso:
        esperar_sucesso_ou_erro(ctx)

    return True


def _aceitar_confirmacao(dialog) -> None:
    logger.info("Caixa de diálogo capturada: {}", dialog.message)
    dialog.accept()
    logger.info("Diálogo aceito.")
