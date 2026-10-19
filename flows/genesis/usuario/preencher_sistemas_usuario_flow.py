"""Vínculos dinâmicos de Sistemas e Perfis do Usuário Genesis."""

from loguru import logger
from playwright.sync_api import Frame, Page

from flows.genesis.shared.preencher_lookup_flow import preencher_campo
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


AVISO_SEM_REGISTRO = "nenhum registro"
SENHA_FALLBACK_POR_POLITICA = "Aa2748838@"
TRECHO_ERRO_POLITICA_SENHA = "A senha deverá conter"


def preencher_sistemas_usuario(page: Page, sistemas: list[dict[str, str]]) -> None:
    """Vincula Sistemas/Perfis e confirma o Usuário com fallback de senha. Cenário A.

    Preserva tentativas de lookup, reuso de linha e descarte de Sistemas indisponíveis.
    A senha alternativa só é aplicada quando o título do campo indica recusa por política.
    """
    logger.info("Iniciou preenchimento de Sistemas e Perfis do Usuário.")
    ctx = escopo(page)
    _vincular_sistemas(page, ctx, sistemas)
    ctx.locator("input[name='cdSistemaSelecionado']").first.check()
    _confirmar_usuario_com_fallback_de_senha(page, ctx)
    logger.info("Finalizou preenchimento de Sistemas e Perfis do Usuário.")


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

    preencher_campo(ctx, "input[name='perfis-1-2']", sistema["perfil"], lookup_name="lookup-perfil-1-2")

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
    """Resolve o Sistema com as duas tentativas de lookup do legado."""
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
            raise RuntimeError(
                f"Aviso inesperado ao consultar o sistema '{nome_sistema}': {aviso}"
            )

        logger.info(
            "Lookup do sistema '{}' não retornou registros (tentativa {}/{}).",
            nome_sistema,
            tentativa,
            tentativas,
        )
        _cancelar_consulta(page, ctx)

    return False


def _texto_do_aviso(ctx: Page | Frame) -> str | None:
    """Lê o aviso visível, retornando None quando ausente ou inacessível."""
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
