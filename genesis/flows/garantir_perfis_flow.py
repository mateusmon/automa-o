from loguru import logger
from playwright.sync_api import Frame, Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_perfil import acessar_perfil
from services.perfil_service import perfil_existe
from utils.espera import aguardar_ajax_global, esperar_sucesso_ou_erro
from utils.sistemas import derivar_nome_perfil
from utils.usuario_logado import obter_nome_usuario_logado
from utils.versao_gen import escopo


def garantir_perfis(context: ExecutionContext) -> None:
    """
    Garante que exista um perfil de teste para cada perfil do usuário logado.

    A origem da cópia não vem mais do blueprint: os perfis de origem são os
    do próprio usuário autenticado na sessão.

    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    prefixo = blueprint.get("prefixo_perfil")

    if not prefixo:
        logger.info("Nenhum 'prefixo_perfil' definido no arquivo yaml. Ignorando fluxo.")
        return

    nome_usuario_logado = obter_nome_usuario_logado(page)

    if not acessar_perfil(page):
        logger.warning("Menu 'Perfil' não disponível para este cliente. Pulando fluxo de perfis.")
        return

    perfis_origem = _obter_perfis_origem(page, nome_usuario_logado, prefixo)
    total = len(perfis_origem)

    logger.info("Foi encontrado um total de {} perfis para o usuário logado.", total)

    for atual, origem in enumerate(perfis_origem, start=1):
        logger.info("Perfil {}/{}", atual, total)

        nome_perfil = derivar_nome_perfil(prefixo, origem["sistema"])

        logger.info(
            "Garantindo perfil nome '{}' (cópia de '{}' — {})",
            nome_perfil,
            origem["nome"],
            origem["sistema"],
        )

        if perfil_existe(page, nome_perfil):
            logger.info("Perfil '{}' já existe. Nenhuma ação necesária.", nome_perfil)
            continue

        logger.info("Perfil '{}' não encontrado. Criando...", nome_perfil)

        if not _criar_perfil(page, nome_usuario_logado, origem, nome_perfil):
            logger.warning(
                "Tabela de módulos veio vazia ao copiar perfil de origem '{}' ({}). "
                "Pulando este sistema.",
                origem["nome"],
                origem["sistema"],
            )
            continue

        if not perfil_existe(page, nome_perfil):
            raise RuntimeError(
                f"Falha ao validar criação de perfil '{nome_perfil}'."
            )

        logger.success("Perfil '{}' criado com sucesso.", nome_perfil)


def perfis_do_usuario(page: Page, nome_usuario: str) -> list[dict]:
    """
    Retorna todos os perfis associados a um usuário.

    Returns:
        Lista de dicionários com as chaves `codigo`, `nome` e `sistema`.
        Lista vazia se o usuário não tiver nenhum perfil.
    """
    if not acessar_perfil(page):
        raise RuntimeError("Falha ao navegar para a tela de Perfil.")

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    filtrar_por_usuario(page, ctx, nome_usuario)

    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    total = int(span_resultado.inner_text().strip())

    perfis: list[dict] = []

    if total > 0:
        tabela = ctx.locator("table[name='paginationTable']")
        tabela.wait_for(state="visible")

        linhas = tabela.locator("tbody tr")
        linhas_visiveis = linhas.count()

        if linhas_visiveis != total:
            logger.warning(
                "A consulta informou {} perfis, mas a grid trouxe {} linhas. "
                "Provável paginação — apenas as linhas visíveis serão consideradas.",
                total,
                linhas_visiveis,
            )

        for num in range(linhas_visiveis):
            linha = linhas.nth(num)
            perfis.append(
                {
                    "codigo": linha.locator("td[columnid='1']").inner_text().strip(),
                    "nome": linha.locator("td[columnid='2']").inner_text().strip(),
                    "sistema": linha.locator("td[columnid='3']").inner_text().strip(),
                }
            )

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return perfis


def filtrar_por_usuario(page: Page, ctx: Page | Frame, nome_usuario: str) -> None:
    """
    Filtra a consulta de perfis pelo usuário informado e executa a busca.
    """
    campo = ctx.locator("input[name='model-3']")
    campo.wait_for(state="visible")
    campo.fill(nome_usuario)

    ctx.locator("button[name='lookup-model-3']").click()
    aguardar_ajax_global(page)

    alerta = ctx.locator(".alert-danger, .alert-warning")
    if alerta.first.is_visible():
        raise RuntimeError(
            f"A consulta de perfis do usuário '{nome_usuario}' retornou um alerta: "
            f"{alerta.first.inner_text()}"
        )

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)


def _obter_perfis_origem(page: Page, nome_usuario_logado: str, prefixo: str) -> list[dict]:
    """
    Busca os perfis do usuário logado que servem de origem para as cópias.
    """
    perfis = perfis_do_usuario(page, nome_usuario_logado)

    if not perfis:
        raise RuntimeError(
            f"O usuário logado '{nome_usuario_logado}' não possui nenhum perfil. "
            "Não há origem para a cópia de perfis."
        )

    prefixo_normalizado = prefixo.strip().upper()
    origem = [
        perfil for perfil in perfis
        if not perfil["nome"].strip().upper().startswith(prefixo_normalizado)
    ]

    descartados = len(perfis) - len(origem)
    if descartados:
        logger.info(
            "{} perfil(is) ignorado(s) por já usarem o prefixo '{}' (cópias anteriores).",
            descartados,
            prefixo,
        )

    if not origem:
        raise RuntimeError(
            f"Todos os perfis do usuário '{nome_usuario_logado}' já usam o prefixo "
            f"'{prefixo}'. Não há perfil de origem válido para copiar."
        )

    _validar_sistemas_unicos(origem)

    return origem


def _validar_sistemas_unicos(perfis: list[dict]) -> None:
    vistos: dict[str, str] = {}

    for perfil in perfis:
        sistema = perfil["sistema"]
        if sistema in vistos:
            raise RuntimeError(
                f"O usuário logado possui mais de um perfil no sistema '{sistema}' "
                f"('{vistos[sistema]}' e '{perfil['nome']}'). "
                "O nome do perfil de teste seria duplicado."
            )
        vistos[sistema] = perfil["nome"]


def _criar_perfil(
    page: Page,
    nome_usuario_logado: str,
    perfil_origem: dict,
    nome_perfil: str,
) -> bool:
    """
    Cria o perfil de teste a partir do perfil de origem.

    Returns:
        True se o perfil foi criado normalmente. False se a tabela de
        módulos veio vazia após "Copiar perfil" — nesse caso a criação é
        abortada  e o chamador deve pular este perfil/sistema.
    """
    if not acessar_perfil(page):
        logger.warning("Menu 'Perfil' não disponível para este cliente. Impossível criar perfil.")
        return False

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    filtrar_por_usuario(page, ctx, nome_usuario_logado)

    _anexar_perfil_de_origem(page, ctx, perfil_origem)

    ctx.get_by_role("button", name="Copiar perfil").click(no_wait_after=True)
    aguardar_ajax_global(page)

    if _tabela_modulos_esta_vazia(ctx):
        return False

    ctx.locator("input[name='nmPerfil']").fill(nome_perfil)
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Confirmar").click(timeout=90_000)
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
    return True


def _tabela_modulos_esta_vazia(ctx: Page | Frame) -> bool:
    """
    Verifica se a tabela "Módulos" veio sem nenhuma linha após "Copiar perfil".
    """
    tabela_modulos = ctx.locator("table.tabela").filter(
        has=ctx.locator("caption div.title", has_text="Módulos")
    )
    linhas = tabela_modulos.locator("tbody tr")
    return linhas.count() == 0


def _anexar_perfil_de_origem(page: Page, ctx: Page | Frame, perfil_origem: dict) -> None:
    # Estamos utilizando o "nome" pois em alguns sistemas o "codigo" está repetido
    nome = perfil_origem["nome"]

    tabela = ctx.locator("table[name='paginationTable']")
    tabela.wait_for(state="visible")

    linhas = tabela.locator("tbody tr")
    total = linhas.count()

    for num in range(total):
        linha = linhas.nth(num)

        if linha.locator("td[columnid='2']").inner_text().strip() != nome:
            continue

        linha.locator("button[name='submitUse']").click(no_wait_after=True)
        aguardar_ajax_global(page)
        return

    raise RuntimeError(
        f"Perfil de origem '{perfil_origem['nome']}' não foi "
        "encontrado na consulta por usuário."
    )