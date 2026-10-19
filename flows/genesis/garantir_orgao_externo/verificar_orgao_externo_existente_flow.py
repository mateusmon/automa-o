from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.corporativo.entidade_externa.cadastro_orgao_externo.navegar_para_orgao_externo_flow import (
    acessar_orgao_externo,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global


def verificar_orgao_externo_existente(
    page: Page, orgaos_externos_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Acessa a tela de órgãos externos e identifica quais itens da massa ainda não existem no sistema."""
    logger.info("Iniciando verificação de órgãos externos existentes...")

    total = len(orgaos_externos_data)
    logger.info("Foi encontrado um total de {} órgãos externos no arquivo yaml.", total)

    orgaos_faltantes = []

    for atual, orgao in enumerate(orgaos_externos_data, start=1):
        logger.info("Verificando órgão externo {}/{}", atual, total)
        nome = orgao["nome"]
        cnpj = orgao["cnpj"]

        logger.info("Garantindo órgão externo CNPJ '{}' ({})", cnpj, nome)

        if _checar_existencia_orgao_externo_no_dom(page, cnpj):
            logger.info(
                "Órgão externo com CNPJ '{}' já existe. Nenhuma ação necessária.", cnpj
            )
        else:
            logger.info(
                "Órgão externo com CNPJ '{}' não encontrado. Marcado para criação.",
                cnpj,
            )
            orgaos_faltantes.append(orgao)

    return orgaos_faltantes


def _checar_existencia_orgao_externo_no_dom(page: Page, cnpj: str) -> bool:
    """Realiza a consulta no modal/tela do sistema e verifica na tabela se o CNPJ está cadastrado."""
    acessar_orgao_externo(page)

    ctx = escopo(page)
    cnpj_formatado = _formatar_cnpj(cnpj)

    # Abrir consulta
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Realizar busca pelo CNPJ no input de consulta
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

    # Ler a tabela e comparar o CNPJ
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


def _formatar_cnpj(cnpj: str) -> str:
    """Formata 14 dígitos como XX.XXX.XXX/XXXX-XX."""
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
