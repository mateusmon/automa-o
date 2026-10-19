from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.corporativo.entidade_externa.cadastro_fornecedor.navegar_para_fornecedor_flow import (
    acessar_fornecedor,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global


def verificar_fornecedor_existente(
    page: Page, fornecedores_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Acessa a tela de fornecedores e identifica quais itens da massa ainda não existem no sistema."""
    logger.info("Iniciando verificação de fornecedores existentes...")

    total = len(fornecedores_data)
    logger.info("Foi encontrado um total de {} fornecedores no arquivo yaml.", total)

    fornecedores_faltantes = []

    for atual, fornecedor in enumerate(fornecedores_data, start=1):
        logger.info("Verificando fornecedor {}/{}", atual, total)
        nome = fornecedor["nome"]
        cnpj = fornecedor["cnpj"]

        logger.info("Garantindo fornecedor nome '{}'", nome)

        if _checar_existencia_fornecedor_no_dom(page, cnpj):
            logger.info("Fornecedor '{}' já existe. Nenhuma ação necessária.", nome)
        else:
            logger.info("Fornecedor '{}' não encontrado. Marcado para criação.", nome)
            fornecedores_faltantes.append(fornecedor)

    return fornecedores_faltantes


def _checar_existencia_fornecedor_no_dom(page: Page, cnpj: str) -> bool:
    """Realiza a consulta no modal/tela do sistema e verifica na tabela se o CNPJ está cadastrado."""
    acessar_fornecedor(page)

    ctx = escopo(page)
    cnpj_formatado = _format_cnpj(cnpj)

    # Abrir consulta
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Realizar busca pelo CNPJ
    ctx.locator("input[name='model-2']").fill(cnpj_formatado)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    # Obter total de registros de acordo com a versão
    if get_versao() >= 4:
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")
        count = int(span_resultado.inner_text().strip())
    else:
        ctx.wait_for_selector("table[name='paginationTable']", timeout=10_000)
        linhas = ctx.locator("table[name='paginationTable'] tbody.scrollBody tr")
        count = linhas.count()

    existe = False

    # Ler a tabela e comparar o texto exato
    if count > 0:
        cnpj_alvo = cnpj_formatado.strip().lower()
        linhas = ctx.locator(
            "table[name='paginationTable'] tbody tr, table tbody tr"
        ).all()

        for linha in linhas:
            celulas = [
                td.inner_text().strip().lower() for td in linha.locator("td").all()
            ]

            if cnpj_alvo in celulas:
                existe = True
                break

    # Fechar tela/modal de consulta
    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe


def _format_cnpj(cnpj: str) -> str:
    """Formata 14 dígitos como XX.XXX.XXX/XXXX-XX."""
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
