from loguru import logger
from playwright.sync_api import Page, expect

from flows.corporativo.estrutura_organizacional.cadastro_almoxarifado.navegar_para_almoxarifado_flow import (
    acessar_almoxarifado,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_almoxarifado_existente(
    page: Page, ug_data: dict, almox_data: list[dict]
) -> list[dict]:
    """Verifica quais almoxarifados da lista ainda não estão cadastrados.

    :param page: Instância da página do Playwright.
    :param ug_data: Dados da Unidade Gestora (UG).
    :param almox_data: Lista de dicionários contendo os almoxarifados.
    :return: Lista com os almoxarifados que não foram encontrados.
    """
    logger.info("Iniciou a verificação de Almoxarifados já criados.")

    almoxarifados_faltantes = []
    total = len(almox_data)
    logger.info("Foi encontrado um total de {} almoxarifados no arquivo yaml.", total)

    for atual, almoxarifado in enumerate(almox_data, start=1):
        logger.info("Almoxarifado {}/{}", atual, total)

        nome_almoxarifado = almoxarifado["nome"]
        sigla_almoxarifado = almoxarifado["sigla"]

        logger.info("Garantindo almoxarifado nome '{}'", nome_almoxarifado)

        if _almoxarifado_existe(page, sigla_almoxarifado):
            logger.info(
                "Almoxarifado '{}' já existe. Nenhuma ação necessária.",
                nome_almoxarifado,
            )
            continue

        almoxarifados_faltantes.append(almoxarifado)

    logger.info("Finalizou a verificação de Almoxarifados já criados.")
    return almoxarifados_faltantes


def _almoxarifado_existe(page: Page, sigla: str) -> bool:
    """Verifica se um almoxarifado com a sigla exata existe no sistema."""
    acessar_almoxarifado(page)
    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Preenche o campo de busca
    campo_sigla = ctx.locator("input[name='model-4']")
    campo_sigla.fill(sigla)

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    # Aguarda o elemento de resultado estar visível
    span_resultado = ctx.locator("span[name='searchResultSize']")
    expect(span_resultado).to_be_visible()

    # Validação segura para converter a contagem em inteiro
    texto_contagem = span_resultado.inner_text().strip()
    count = int(texto_contagem) if texto_contagem.isdigit() else 0

    existe = False

    if count > 0:
        sigla_alvo = sigla.strip()

        # Localiza diretamente se existe alguma linha da tabela que contém exatamente a sigla nas células
        # Evita a iteração manual com `.all()` que é propensa a desacoplamento do DOM
        linha_encontrada = ctx.locator("table tbody tr").filter(
            has=ctx.locator("td", has_text=sigla_alvo)
        )

        # Confirma se o texto bate exatamente em alguma célula da linha
        for td in linha_encontrada.locator("td").all_inner_texts():
            if td.strip().lower() == sigla_alvo.lower():
                existe = True
                break

    # Garante a limpeza do estado da tela
    btn_cancelar = ctx.get_by_role("button", name="Cancelar")
    if btn_cancelar.is_visible():
        btn_cancelar.click()
        aguardar_ajax_global(page)

    return existe
