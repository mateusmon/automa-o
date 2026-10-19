import re

from loguru import logger
from playwright.sync_api import Page, expect

from flows.genesis.shared.clicar_botao_com_retry_flow import clicar_botao_com_retry
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def remover_restricoes_perfil(page: Page, indice: int, total: int) -> None:
    """
    Abre o Perfil da linha `indice` da consulta atual, percorre todos os seus módulos
    e funcionalidades removendo as restrições encontradas e confirma — mesma
    sequência de uma iteração de `_remover_restricoes` do legado. Os loops de
    módulos e funcionalidades ficam juntos porque dependem do mesmo Perfil aberto.

    Pressupõe a grid de resultados aberta (ver `consultar_perfis_por_usuario`).
    Ao final a tela fica no Perfil confirmado; o chamador deve consultar de novo
    antes de abrir o próximo.
    """
    ctx = escopo(page)

    # Re-query e sincronização da tabela no início de cada iteração
    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")

    tabela = ctx.locator("table[name='paginationTable']")
    tabela.wait_for(state="visible")

    linha = tabela.locator("tbody tr").nth(indice)
    celula_perfil = linha.locator("td[columnid='3']")
    celula_perfil.wait_for(state="visible")

    nome_perfil = celula_perfil.inner_text().strip()
    logger.info("Processando perfil {}({}/{}).", nome_perfil, indice + 1, total)

    linha.locator("button[name='submitUse']").click(no_wait_after=True)
    aguardar_ajax_global(page)

    _verificar_modulos(page)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _verificar_modulos(page: Page) -> None:
    """
    Percorre todos os módulos do perfil aberto e delega o processamento
    de restrições para _verificar_funcionalidades.

    Se o módulo não tiver funcionalidades disponíveis, a aplicação exibe
    um erro — nesse caso o módulo é pulado via continue.
    """
    ctx = escopo(page)
    # Esperando até a caption Módulos da tabela ficar visível
    expect(ctx.locator("caption", has_text=re.compile(r"módulo", re.IGNORECASE))).to_be_visible(timeout=300_000)

    ctx.locator("table.tabela tbody tr").first.wait_for(state="visible")

    modulos = ctx.locator("table.tabela tbody tr").count()
    logger.info("Encontrado(s) {} módulo(s) para processar.", modulos)

    for num in range(modulos):
        # Esperando até a caption Módulos da tabela ficar visível
        expect(ctx.locator("caption", has_text=re.compile(r"módulo", re.IGNORECASE))).to_be_visible(timeout=300_000)

        botao = ctx.locator("table.tabela tbody tr").nth(num).locator("button[name^=edit-contexto]")
        resultado = clicar_botao_com_retry(page, botao, "table[name^='div']")

        if resultado:
            logger.info("Módulo {}/{} sem funcionalidades ({}). Pulando.", num + 1, modulos, resultado)
            if resultado == "alt_erro":
                ctx.get_by_role("button", name="Cancelar").click()
                aguardar_ajax_global(page)
            continue

        logger.info("Verificando funcionalidades do módulo {}/{}.", num + 1, modulos)
        _verificar_funcionalidades(page)


def _verificar_funcionalidades(page: Page) -> None:
    """
    Percorre todas as funcionalidades do módulo aberto e clica no
    checkbox das que contêm 'RESTRINGIR' ou 'ANÁLISE' no nome.
    """
    ctx = escopo(page)

    tabela = ctx.locator("table[name^='div']")
    tabela.locator("tbody tr").first.wait_for(state="visible", timeout=3_000)
    count = tabela.locator("tbody tr").count()

    for num in range(count):
        linha = tabela.locator("tbody tr").nth(num)
        input_nome = linha.locator("input[bind='nmFuncionalidade']")
        if input_nome.count() == 0:
            continue
        # O texto da funcionalidade está no atributo value do input, não no texto visível do DOM
        valor = input_nome.input_value()
        if "RESTRINGIR" in valor or "ANÁLISE" in valor or "ANALISE" in valor:
            logger.info("Removendo restrição: '{}'.", valor)
            linha.locator("input[type=checkbox]").click()

    ctx.get_by_role("button", name="Retornar").click()
    aguardar_ajax_global(page)
