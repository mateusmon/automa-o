from typing import Any

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    escolher_cidade,
    esperar_sucesso_ou_erro,
    select_tipo,
)


def criar_fornecedor(page: Page, fornecedores_faltantes: list[dict[str, Any]]) -> None:
    """Realiza o cadastro determinístico de todos os fornecedores pendentes."""
    if not fornecedores_faltantes:
        return

    logger.info(f"Iniciando criação de {len(fornecedores_faltantes)} fornecedor(es)...")

    for fornecedor in fornecedores_faltantes:
        logger.info("Criando fornecedor '{}'...", fornecedor["nome"])
        _preencher_formulario_fornecedor(page, fornecedor)

    logger.info("Criação de fornecedores concluída.")


def _preencher_formulario_fornecedor(
    page: Page, fornecedor_data: dict[str, Any]
) -> None:
    """Preenche os campos da interface para um único fornecedor."""
    tipo = fornecedor_data["tipo"]
    porte = fornecedor_data["porte"]
    nome = fornecedor_data["nome"]
    cnpj = fornecedor_data["cnpj"]
    endereco = fornecedor_data["endereco"]
    bairro = fornecedor_data["bairro"]
    cidade = fornecedor_data["cidade"]
    fone = fornecedor_data["fone"]

    ctx = escopo(page)

    if ctx.locator("input[name='nrIdentAgente']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    select_tipo(ctx, "situacaoJuridica", tipo)
    select_tipo(ctx, "cdTpForPorte", porte)

    ctx.locator("input[name='inCartorio'][value='N']").check()
    aguardar_ajax_global(page)

    ctx.locator("input[name='nrIdentAgente']").fill(_formatar_cnpj(cnpj))
    ctx.locator("input[name='nmRazaoSocialGeral']").fill(nome)
    ctx.locator("input[name='nmAgente']").fill(nome)
    ctx.locator("input[name='edAgente']").fill(endereco)
    ctx.locator("input[name='nmBairro']").fill(bairro)

    escolher_cidade(ctx, cidade)

    ctx.locator("input[name='nrDdd1']").fill("61")
    ctx.locator("input[name='nrFone1']").fill(fone)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _formatar_cnpj(cnpj: str) -> str:
    """Formata 14 dígitos como XX.XXX.XXX/XXXX-XX."""
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
