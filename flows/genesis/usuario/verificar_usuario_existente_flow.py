"""Verificação da identidade do Usuário, sem anexar nem alterar registros."""

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_usuario_existente(page: Page, nome: str) -> bool:
    """Verifica a consulta aberta pela regra do service legado e a cancela.

    Compara cada célula ignorando caixa e removendo o prefixo ``código - ``.
    Não anexa registros, não detecta duplicatas e não aceita nomes mascarados.
    Deve ser chamado somente quando consultar_usuario retornar True; o aviso
    de funcionário ausente é tratado naquela consulta, sem cancelar.
    """
    logger.info("Iniciou verificação de Usuário '{}'.", nome)
    ctx = escopo(page)
    resultado = ctx.locator("span[name='searchResultSize']")
    resultado.wait_for(state="visible")
    existe = False
    if int(resultado.inner_text().strip()) > 0:
        nome_alvo = nome.strip().lower()
        for linha in ctx.locator("table tbody tr").all():
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]
            if any(celula.split(" - ", 1)[-1].strip() == nome_alvo for celula in celulas):
                existe = True
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)
    logger.info("Finalizou verificação de Usuário '{}': {}.", nome, existe)
    return existe
