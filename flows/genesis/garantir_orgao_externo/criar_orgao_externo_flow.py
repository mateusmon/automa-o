from typing import Any

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    escolher_cidade,
    esperar_sucesso_ou_erro,
)


def criar_orgao_externo(page: Page, orgaos_faltantes: list[dict[str, Any]]) -> None:
    """Realiza o cadastro determinístico de todos os órgãos externos pendentes."""
    if not orgaos_faltantes:
        return

    logger.info(f"Iniciando criação de {len(orgaos_faltantes)} órgão(s) externo(s)...")

    for orgao in orgaos_faltantes:
        logger.info("Criando órgão externo '{}'...", orgao["nome"])
        _preencher_formulario_orgao_externo(page, orgao)

    logger.info("Criação de órgãos externos concluída.")


def _preencher_formulario_orgao_externo(page: Page, orgao_data: dict[str, Any]) -> None:
    """Preenche os campos da interface para um único órgão externo."""
    ctx = escopo(page)
    aguardar_ajax_global(page)

    if ctx.locator("input[name='nrIdentAgente']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='nrIdentAgente']").wait_for(state="visible")

    ctx.locator("input[name='nrIdentAgente']").fill(_formatar_cnpj(orgao_data["cnpj"]))
    ctx.locator("input[name='nmAgente']").fill(orgao_data["nome"])
    ctx.locator("input[name='sgOrgaoExterno']").fill(orgao_data["sigla"])
    ctx.locator("input[name='edAgente']").fill(orgao_data["endereco"])
    ctx.locator("input[name='nmBairro']").fill(orgao_data["bairro"])

    escolher_cidade(ctx, orgao_data["cidade"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _formatar_cnpj(cnpj: str) -> str:
    """Formata 14 dígitos como XX.XXX.XXX/XXXX-XX."""
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
