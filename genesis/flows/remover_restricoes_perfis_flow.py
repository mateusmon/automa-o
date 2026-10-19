import re

from loguru import logger
from playwright.sync_api import Page, expect

from engine.execution_context import ExecutionContext
from navigation.navegar_para_perfil import acessar_perfil
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.inputs import clicar_botao_com_retry
from utils.versao_gen import escopo


def remover_restricoes_perfis(context: ExecutionContext) -> None:
    """
    Remove restrições de funcionalidades de todos os perfis associados
    ao primeiro usuário definido no blueprint.

    Navega para a tela de perfis, consulta os perfis do usuário e, para
    cada perfil, percorre todos os módulos e funcionalidades removendo
    as restrições encontradas.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    usuarios = blueprint.get("usuarios")

    if not usuarios:
        logger.info("Nenhum usuário definido no arquivo yaml. Ignorando fluxo.")
        return
    
    logger.info("Removendo restrições dos perfis.")

    acessar_perfil(page)
    _consultar_perfis(page, usuarios)
    sucesso = _remover_restricoes(page, usuarios)

    if not sucesso:
        logger.error("Falha ao remover restrições de perfis.")
        raise RuntimeError("Falha ao remover restrições de perfis.")
    
    logger.success("Restrições removidas com sucesso")


def _consultar_perfis(page: Page, usuarios: list[dict]) -> None:
    """
    Abre o painel de consulta e filtra os perfis pelo nome do primeiro
    usuário do blueprint.

    Apenas o primeiro usuário é usado como filtro porque todos os usuários
    do blueprint compartilham os mesmos perfis.
    """
    ctx = escopo(page)
    primeiro_usuario = usuarios[0]
    nome_usuario = primeiro_usuario["nome"]

    logger.info("Consultando perfis do usuário '{}'.", nome_usuario)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-3']", nome_usuario)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)


def _remover_restricoes(page: Page, usuarios: list[dict]) -> bool:
    """
    Itera sobre todos os perfis retornados pela consulta e remove as
    restrições de cada um.

    Para cada perfil: abre o registro, chama _verificar_modulos para
    processar as restrições, confirma e volta para a listagem.

    Retorna False se nenhum perfil for encontrado na consulta.
    """
    ctx = escopo(page)
    try:
        # Esse span é populado pelo banco e é a fonte confiável do total de resultados
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")

        if span_resultado.inner_text() == "0":
            logger.info("Não há perfis para este usuário.")
            return False
    except Exception:
        logger.info("Erro inesperado. Provavelmente não chegou à página de resultado de consulta de perfis.")
        return False

    tabela = ctx.locator("table[name='paginationTable']")
    tabela.wait_for(state="visible")

    total_perfis = tabela.locator("tbody tr").count()
    logger.info("Encontrado(s) {} perfil(is) para processar.", total_perfis)

    for num in range(total_perfis):
        # Re-query e sincronização da tabela no início de cada iteração
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")
        
        tabela = ctx.locator("table[name='paginationTable']")
        tabela.wait_for(state="visible")

        linha = tabela.locator("tbody tr").nth(num)
        celula_perfil = linha.locator("td[columnid='3']")
        celula_perfil.wait_for(state="visible")
        
        nome_perfil = celula_perfil.inner_text().strip()
        logger.info("Processando perfil {}({}/{}).", nome_perfil, num + 1, total_perfis)

        linha.locator("button[name='submitUse']").click(no_wait_after=True)
        aguardar_ajax_global(page)

        _verificar_modulos(page)

        ctx.get_by_role("button", name="Confirmar").click()
        aguardar_ajax_global(page)
        esperar_sucesso_ou_erro(ctx)

        # Atualização: Consulta e aguarda obrigatoriamente a finalização da requisição AJAX
        _consultar_perfis(page, usuarios)
        aguardar_ajax_global(page)

    return True
    

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
    Percorre todas as funcionalidades do módulo aberto e desmarca o
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
