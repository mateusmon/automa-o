from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_fornecedor import acessar_fornecedor
from services.fornecedor_service import fornecedor_existe
from utils.espera import (
    aguardar_ajax_global,
    escolher_cidade,
    esperar_sucesso_ou_erro,
    select_tipo,
)
from utils.versao_gen import escopo


def garantir_fornecedores(context: ExecutionContext) -> None:
    """
    Ensures fornecedores exists according to blueprint.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    fornecedores_data = blueprint.get("fornecedores")

    if not fornecedores_data:
        logger.info("Nenhum fornecedor definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_fornecedor(page):
        logger.error("Menu 'Fornecedor' não disponível para este cliente.")
        return

    total = len(fornecedores_data)
    logger.info("Foi encontrado um total de {} fornecedores no arquivo yaml.", total)

    for atual, fornecedor in enumerate(fornecedores_data, start=1):
        logger.info("Fornecedor {}/{}", atual, total)

        nome_fornecedor = fornecedor["nome"]
        cnpj = fornecedor["cnpj"]

        logger.info("Garantindo fornecedor nome '{}'", nome_fornecedor)

        if fornecedor_existe(page, cnpj):
            logger.info("Fornecedor '{}' já existe. Nenhuma ação necessária.", nome_fornecedor)
            continue

        logger.info("Fornecedor '{}' não encontrado. Criando...", nome_fornecedor)

        _criar_fornecedor(page, fornecedor)

        # --- Post-creation validation ---
        if not fornecedor_existe(page, cnpj):
            raise RuntimeError(
                f"Falha ao validar criação de fornecedor '{nome_fornecedor}'."
            )

        logger.success("Fornecedor '{}' criado com sucesso.", nome_fornecedor)


def _criar_fornecedor(page: Page, fornecedor_data: dict) -> None:
    """
    Performs deterministic creation of fornecedor.
    Assumes prior existence check returned False.
    """
    tipo = fornecedor_data["tipo"]
    porte = fornecedor_data["porte"]
    nome = fornecedor_data["nome"]
    cnpj = fornecedor_data["cnpj"]
    endereco = fornecedor_data["endereco"]
    bairro = fornecedor_data["bairro"]
    cidade = fornecedor_data["cidade"]
    fone = fornecedor_data["fone"]

    if not acessar_fornecedor(page):
        logger.error("Menu 'Fornecedor' não disponível para este cliente.")
        return

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
