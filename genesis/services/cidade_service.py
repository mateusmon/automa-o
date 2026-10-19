from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_cidade import acessar_cidade
from utils.espera import (
    aguardar_ajax_global,
    gerar_variacoes_nome,
)
from utils.versao_gen import escopo


def cidade_existe(page: Page, nome: str) -> bool:
    """
    Verifica se a cidade existe na base de dados, testando variações do nome
    (ex: com/sem acento) caso não encontre na primeira tentativa.
    """
    # Navigation
    if not acessar_cidade(page):
        return False

    ctx = escopo(page)

    variacoes = gerar_variacoes_nome(nome)
    existe = False

    for tentativa, variacao in enumerate(variacoes, start=1):
        campo_sigla = ctx.locator("#model-1")

        if not campo_sigla.is_visible():
            btn_consulta = ctx.get_by_role("button", name="Consulta", exact=True)
            if btn_consulta.is_visible():
                btn_consulta.click()
                aguardar_ajax_global(page)
            else:
                btn_novo = ctx.get_by_title("Consultar novo registro")
                if btn_novo.is_visible():
                    btn_novo.last.click()
                    aguardar_ajax_global(page)

                if not campo_sigla.is_visible():
                    btn_cancelar = ctx.get_by_role("button", name="Cancelar")
                    if btn_cancelar.is_visible():
                        btn_cancelar.click()
                        aguardar_ajax_global(page)

                    if btn_consulta.is_visible():
                        btn_consulta.click()
                        aguardar_ajax_global(page)

        campo_sigla.wait_for(state="visible", timeout=5_000)
        campo_sigla.clear()
        campo_sigla.fill(variacao)

        ctx.get_by_title("Consultar novo registro").click()
        aguardar_ajax_global(page)

        # Verificar quantidade de resultados
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible", timeout=5_000)
        count = int(span_resultado.inner_text().strip())

        # Ler a tabela e comparar o texto exato
        if count > 0:
            variacao_alva = variacao.strip().lower()
            linhas = ctx.locator("table tbody tr").all()

            for linha in linhas:
                celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

                if variacao_alva in celulas:
                    existe = True
                    break

        if existe:
            if variacao != nome:
                logger.info("Cidade encontrada como '{}' (busca original '{}'). Total de registros: {}", variacao, nome, count)
            else:
                logger.info("Cidade '{}' encontrada. Total de registros: {}", variacao, count)
            break
        else:
            logger.debug("Consulta por '{}' retornou 0 resultados exatos. Tentando próxima variação...", variacao)

    btn_cancelar = ctx.get_by_role("button", name="Cancelar")
    if btn_cancelar.is_visible():
        btn_cancelar.click()
        aguardar_ajax_global(page)

    return existe
