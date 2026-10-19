from engine.execution_context import ExecutionContext
from flows.garantir_perfis_flow import perfis_do_usuario
from loguru import logger
from navigation.navegar_para_perfil import acessar_perfil
from navigation.navegar_para_usuario import acessar_usuario
from playwright.sync_api import Frame, Page
from services.usuario_service import usuario_existe
from utils.dados_locais import usuarios_para_garantir
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.sistemas import (
    derivar_nome_perfil,
    nome_do_sistema,
)
from utils.usuario_logado import obter_nome_usuario_logado
from utils.versao_gen import escopo

AVISO_SEM_REGISTRO = "nenhum registro"
SENHA_FALLBACK_POR_POLITICA = "Aa2748838@"
TRECHO_ERRO_POLITICA_SENHA = "A senha deverá conter"


def garantir_usuarios(context: ExecutionContext) -> None:
    """
    Ensures usuario exists according to blueprint.

    Os perfis vinculados não vêm do blueprint: são os criados pelo
    `garantir_perfis`, derivados dos perfis do usuário logado. A lista é
    redescoberta aqui para não exigir estado compartilhado entre flows.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    usuarios_data = usuarios_para_garantir(context)

    if not usuarios_data:
        logger.info("Nenhum usuário definido no blueprint ou local. Ignorando fluxo.")
        return

    prefixo = blueprint.get("prefixo_perfil")

    if not prefixo:
        logger.info("Nenhum 'prefixo_perfil' definido no arquivo yaml. Ignorando fluxo.")
        return

    sistemas = _montar_sistemas(page, prefixo)

    if sistemas is None:
        logger.warning("Sem perfis para vincular neste cliente. Pulando fluxo de usuários.")
        return

    if not acessar_usuario(page):
        logger.warning(
            "Menu 'Usuário' não disponível para este cliente. Pulando fluxo de usuários."
        )
        return

    total = len(usuarios_data)

    logger.info("Foi encontrado um total de {} usuários para garantir.", total)

    for atual, usuario in enumerate(usuarios_data, start=1):
        logger.info("Usuário {}/{}", atual, total)

        nome = usuario["nome"]

        logger.info("Garantindo Usuário com nome '{}'", nome)

        if usuario_existe(page, nome):
            logger.info("Usuário '{}' já existe. Nenhuma ação necesária.", nome)
            continue

        logger.info("Usuário '{}' não encontrado. Criando...", nome)

        _criar_usuario(page, usuario, sistemas)

        if not usuario_existe(page, nome):
            raise RuntimeError(f"Falha ao validar criação do usuário '{nome}'.")

        logger.success("Usuário '{}' criado com sucesso.", nome)


def _montar_sistemas(page: Page, prefixo: str) -> list[dict[str, str]] | None:
    """
    Monta os pares sistema/perfil a vincular.

    Returns:
        A lista de pares, ou `None` se o menu 'Perfil' não existir no cliente.
    """
    nome_usuario_logado = obter_nome_usuario_logado(page)

    if not acessar_perfil(page):
        logger.warning("Menu 'Perfil' não disponível para este cliente.")
        return None

    perfis = perfis_do_usuario(page, nome_usuario_logado)

    prefixo_normalizado = prefixo.strip().upper()
    origem = [
        perfil
        for perfil in perfis
        if not perfil["nome"].strip().upper().startswith(prefixo_normalizado)
    ]

    if not origem:
        raise RuntimeError(
            f"Nenhum perfil de origem encontrado para o usuário logado "
            f"'{nome_usuario_logado}'. Não há perfis para vincular."
        )

    sistemas = [
        {
            "nome": nome_do_sistema(perfil["sistema"]),
            "perfil": derivar_nome_perfil(prefixo, perfil["sistema"]),
        }
        for perfil in origem
    ]

    logger.info("{} perfil(is) serão vinculados a cada usuário.", len(sistemas))

    return sistemas


def _criar_usuario(page: Page, usuario_data: dict, sistemas: list[dict[str, str]]) -> None:
    """
    Performs deterministic creation of usuario.
    Assumes prior existence check returned False.
    """
    if not acessar_usuario(page):
        logger.warning("Menu 'Usuário' não disponível para este cliente. Impossível criar usuário.")
        return

    usuario_data = dict(usuario_data)
    usuario_data.setdefault("nome", usuario_data.get("usuario") or usuario_data.get("login"))

    ctx = escopo(page)
    senha = usuario_data["senha"]

    _abrir_formulario(page, ctx)

    preencher_campo(ctx, "input[name='funcionario']", usuario_data["nome"])

    ctx.locator("input[name='senha']").fill(senha)
    ctx.locator("input[name='confirmacaoSenha']").fill(senha)

    _vincular_sistemas(page, ctx, sistemas)

    ctx.locator("input[name='cdSistemaSelecionado']").first.check()
    _confirmar_usuario_com_fallback_de_senha(page, ctx)


def _confirmar_usuario_com_fallback_de_senha(page: Page, ctx: Page | Frame) -> None:
    """Confirma o usuário e reaplica a senha forte somente se a política a rejeitar."""
    try:
        ctx.get_by_role("button", name="Confirmar").click()
        aguardar_ajax_global(page)
        esperar_sucesso_ou_erro(ctx)
        return
    except RuntimeError:
        erro_senha = ctx.locator("input[name='senha']").get_attribute("title") or ""
        if TRECHO_ERRO_POLITICA_SENHA not in erro_senha:
            raise

    logger.warning("Senha padrão rejeitada pela política do cliente. Tentando senha de fallback.")
    ctx.locator("input[name='senha']").fill(SENHA_FALLBACK_POR_POLITICA)
    ctx.locator("input[name='confirmacaoSenha']").fill(SENHA_FALLBACK_POR_POLITICA)
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _abrir_formulario(page: Page, ctx: Page | Frame) -> None:
    """
    Garante que o formulário de cadastro esteja aberto e editável.

    """
    campo = ctx.locator("input[name='funcionario']")

    try:
        campo.wait_for(state="visible", timeout=5_000)
        if not campo.is_disabled():
            return
    except Exception:
        logger.debug("Formulário de usuário não está aberto. Clicando em 'Novo'.")

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)

    campo.wait_for(state="visible", timeout=30_000)


def _vincular_sistemas(page: Page, ctx: Page | Frame, sistemas: list[dict[str, str]]) -> None:
    """
    Adiciona uma linha por sistema e vincula o perfil correspondente.

    A tela de Usuário só oferece os sistemas habilitados para atribuição no
    cliente. Sistemas indisponíveis são pulados.

    Raises:
        RuntimeError: Se nenhum sistema puder ser vinculado.
    """
    indice = 0
    linha_reaproveitavel = False
    vinculados: list[str] = []
    pulados: list[str] = []

    for sistema in sistemas:
        if not linha_reaproveitavel:
            indice += 1
            aguardar_ajax_global(page)
            ctx.get_by_title("Adicionar Linhas").click()
            aguardar_ajax_global(page)

        if _associar_perfil(page, ctx, sistema, indice):
            vinculados.append(sistema["nome"])
            linha_reaproveitavel = False
            continue

        logger.warning(
            "Sistema '{}' não disponível para vínculo neste cliente. "
            "Perfil '{}' não será vinculado.",
            sistema["nome"],
            sistema["perfil"],
        )
        pulados.append(sistema["nome"])
        linha_reaproveitavel = True

    if pulados:
        logger.info("{} sistema(s) pulado(s): {}.", len(pulados), ", ".join(pulados))

    if not vinculados:
        raise RuntimeError(
            "Nenhum sistema pôde ser vinculado ao usuário. Sistemas tentados: "
            f"{', '.join(sistema['nome'] for sistema in sistemas)}."
        )

    logger.info("{} sistema(s) vinculado(s): {}.", len(vinculados), ", ".join(vinculados))


def _associar_perfil(page: Page, ctx: Page | Frame, sistema: dict[str, str], indice: int) -> bool:
    """
    Preenche o sistema da linha `indice` e vincula o perfil.

    Returns:
        False se o sistema não está disponível para vínculo neste cliente.
    """
    if not _preencher_sistema(page, ctx, indice, sistema["nome"]):
        return False

    ctx.locator(f"button[name='edit-sistemas-{indice}-5']").click()
    aguardar_ajax_global(page)

    preencher_campo(
        ctx, "input[name='perfis-1-2']", sistema["perfil"], lookup_name="lookup-perfil-1-2"
    )

    ctx.locator("input[name='cdPerfilSelecionado']").check()
    ctx.get_by_role("button", name="Retornar").click()
    aguardar_ajax_global(page)

    return True


def _preencher_sistema(
    page: Page,
    ctx: Page | Frame,
    indice: int,
    nome_sistema: str,
    tentativas: int = 2,
) -> bool:

    campo = ctx.locator(f"input[name='sistemas-{indice}-2']")

    for tentativa in range(1, tentativas + 1):
        campo.wait_for(state="visible", timeout=30_000)
        campo.fill(nome_sistema)

        ctx.locator(f"button[name='lookup-sistemas-{indice}-2']").click()
        aguardar_ajax_global(page)

        aviso = _texto_do_aviso(ctx)

        if aviso is None:
            return True

        if AVISO_SEM_REGISTRO not in aviso.lower():
            raise RuntimeError(f"Aviso inesperado ao consultar o sistema '{nome_sistema}': {aviso}")

        logger.info(
            "Lookup do sistema '{}' não retornou registros (tentativa {}/{}).",
            nome_sistema,
            tentativa,
            tentativas,
        )
        _cancelar_consulta(page, ctx)

    return False


def _texto_do_aviso(ctx: Page | Frame) -> str | None:

    aviso = ctx.locator("div[name='divWarningMsg'], .alert-warning").first

    try:
        if not aviso.is_visible():
            return None
        return aviso.inner_text().strip()
    except Exception:
        return None


def _cancelar_consulta(page: Page, ctx: Page | Frame) -> None:
    """Volta da tela "Consultar Sistema" para o cadastro do usuário."""
    botao = ctx.get_by_role("button", name="Cancelar")

    try:
        if not botao.first.is_visible():
            logger.debug("Botão 'Cancelar' não visível. Nada a cancelar.")
            return
    except Exception:
        return

    botao.first.click()
    aguardar_ajax_global(page)
