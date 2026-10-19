"""Leitura e formatação das competências financeiras abertas no ASI."""

from calendar import monthrange
from datetime import date
import re
from typing import Literal, TypeAlias

from loguru import logger
from playwright.sync_api import Page, expect


FormatoData: TypeAlias = Literal["DD/MM/YYYY", "DDMMYYYY", "YYYYMM", "YYYY/MM"]
ModuloFinanceiro: TypeAlias = Literal["almoxarifado", "patrimonio"]

_FORMATO_PADRAO: FormatoData = "DD/MM/YYYY"
_FORMATOS_VALIDOS: tuple[FormatoData, ...] = (
    "DD/MM/YYYY",
    "DDMMYYYY",
    "YYYYMM",
    "YYYY/MM",
)
_SELETORES_USUARIO = (
    "#centralHeaderUserName",
    "button[title='Usuário']",
)
_SELETORES_FECHAR_PAINEL = (
    "#centralHeaderUserContentCloseButton",
    "#tplPanelUser button:has-text('x')",
)
_SELETORES_COMPETENCIA: dict[ModuloFinanceiro, tuple[str, ...]] = {
    "almoxarifado": (
        "#anoMesAlmox-centralHeaderUserContent + span",
        "#tplPanelUser p:has-text('Almoxarifado. Ano/Mês aberto U.G.:') + span",
    ),
    "patrimonio": (
        "[id*='anoMes'][id*='centralHeaderUserContent']"
        ":not(#anoMesAlmox-centralHeaderUserContent) + span",
        "#tplPanelUser p:has-text('Patrimonio. Ano/Mês aberto U.G.:') + span",
    ),
}


def obter_data_almoxarifado(
    page: Page,
    formato: FormatoData = _FORMATO_PADRAO,
) -> str:
    """Obtém a data ou competência aberta do Almoxarifado.

    Args:
        page: Página Playwright autenticada no ASI.
        formato: Formato desejado para o retorno.

    Returns:
        Data ou competência do Almoxarifado no formato solicitado. Quando a leitura
        da interface falha, devolve a data civil atual e registra um warning.
    """
    return _obter_data(page, "almoxarifado", formato)


def obter_data_patrimonio(
    page: Page,
    formato: FormatoData = _FORMATO_PADRAO,
) -> str:
    """Obtém a data ou competência aberta do Patrimônio.

    Args:
        page: Página Playwright autenticada no ASI.
        formato: Formato desejado para o retorno.

    Returns:
        Data ou competência do Patrimônio no formato solicitado. Quando a leitura
        da interface falha, devolve a data civil atual e registra um warning.
    """
    return _obter_data(page, "patrimonio", formato)


def _obter_data(page: Page, modulo: ModuloFinanceiro, formato: FormatoData) -> str:
    """Lê e formata a competência do módulo, com fallback para o relógio local."""
    _validar_formato(formato)
    hoje = date.today()

    try:
        ano, mes = _obter_competencia(page, modulo)
    except Exception as erro:
        logger.warning(
            "Não foi possível obter a competência de {} ({}: {}). "
            "Usando a data civil atual.",
            modulo,
            type(erro).__name__,
            erro,
        )
        ano, mes = hoje.year, hoje.month

    resultado = _formatar_competencia(ano, mes, formato, hoje)
    logger.debug(
        "Competência de {} formatada como {}: {}.",
        modulo,
        formato,
        resultado,
    )
    return resultado


def _obter_competencia(page: Page, modulo: ModuloFinanceiro) -> tuple[int, int]:
    """Lê a competência no DOM e abre o painel apenas quando necessário."""
    seletores = _SELETORES_COMPETENCIA[modulo]
    erro_leitura_fechada: Exception | None = None

    try:
        return _ler_competencia(page, seletores)
    except Exception as erro:
        erro_leitura_fechada = erro

    painel_aberto = _algum_visivel(page, _SELETORES_FECHAR_PAINEL)
    abriu_painel = False

    try:
        if not painel_aberto:
            _clicar_primeiro_visivel(page, _SELETORES_USUARIO)
            abriu_painel = True
        return _ler_competencia(page, seletores, aguardar_valor=True)
    except Exception as erro:
        raise RuntimeError(
            f"Falha ao ler a competência de {modulo} com o painel fechado "
            f"({erro_leitura_fechada}) e aberto ({erro})."
        ) from erro
    finally:
        if abriu_painel:
            _clicar_primeiro_visivel(page, _SELETORES_FECHAR_PAINEL, obrigatorio=False)


def _ler_competencia(
    page: Page,
    seletores: tuple[str, ...],
    *,
    aguardar_valor: bool = False,
) -> tuple[int, int]:
    """Lê e valida um valor de competência a partir do DOM."""
    erros: list[str] = []
    for seletor in seletores:
        elemento = page.locator(seletor)
        if elemento.count() == 0:
            erros.append(f"{seletor!r}: não encontrado")
            continue

        try:
            alvo = elemento.first
            if aguardar_valor:
                expect(alvo).to_have_text(re.compile(r"\s*\d{6}\s*"), timeout=2_000)
            valor = alvo.text_content(timeout=2_000)
            return _interpretar_competencia(valor)
        except Exception as erro:
            erros.append(f"{seletor!r}: {erro}")

    raise LookupError("; ".join(erros))


def _algum_visivel(page: Page, seletores: tuple[str, ...]) -> bool:
    """Informa se algum dos seletores possui um elemento visível."""
    return any(
        page.locator(seletor).first.is_visible()
        for seletor in seletores
        if page.locator(seletor).count() > 0
    )


def _clicar_primeiro_visivel(
    page: Page,
    seletores: tuple[str, ...],
    *,
    obrigatorio: bool = True,
) -> bool:
    """Clica no primeiro seletor visível sem aguardar alternativas ausentes."""
    for seletor in seletores:
        elemento = page.locator(seletor)
        if elemento.count() > 0 and elemento.first.is_visible():
            elemento.first.click()
            return True

    if obrigatorio:
        raise LookupError(f"Nenhum elemento visível entre: {seletores!r}")
    return False


def _interpretar_competencia(valor: str | None) -> tuple[int, int]:
    """Converte `YYYYMM` ou `YYYY/MM` em ano e mês validados."""
    texto = (valor or "").strip()
    correspondencia = re.fullmatch(r"(\d{4})/?(\d{2})", texto)
    if correspondencia is None:
        raise ValueError(f"Competência inválida: {texto!r}")

    ano, mes = map(int, correspondencia.groups())
    try:
        date(ano, mes, 1)
    except ValueError as erro:
        raise ValueError(f"Competência inválida: {texto!r}") from erro
    return ano, mes


def _formatar_competencia(
    ano: int,
    mes: int,
    formato: FormatoData,
    hoje: date,
) -> str:
    """Formata a competência, aplicando a regra de data financeira acordada."""
    _validar_formato(formato)
    date(ano, mes, 1)

    if formato == "YYYYMM":
        return f"{ano:04d}{mes:02d}"
    if formato == "YYYY/MM":
        return f"{ano:04d}/{mes:02d}"

    if (ano, mes) == (hoje.year, hoje.month):
        data_referencia = hoje
    else:
        ultimo_dia = monthrange(ano, mes)[1]
        data_referencia = date(ano, mes, ultimo_dia)

    if formato == "DDMMYYYY":
        return data_referencia.strftime("%d%m%Y")
    return data_referencia.strftime("%d/%m/%Y")


def _validar_formato(formato: str) -> None:
    """Rejeita formatos não suportados como erro de programação."""
    if formato not in _FORMATOS_VALIDOS:
        formatos = ", ".join(_FORMATOS_VALIDOS)
        raise ValueError(f"Formato inválido: {formato!r}. Use um de: {formatos}.")
