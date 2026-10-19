from loguru import logger
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def preencher_patrimonio(page: Page) -> None:
    logger.info("Iniciou preenchimento de patrimonio.")

    ctx = escopo(page)
    _preencher(ctx, 2)
    _preencher(ctx, 3)
    
    logger.info("Finalizou preenchimento de patrimonio.")


def clicar_primeira_linha_se_existir(ctx, timeout_ms: int = 5000) -> bool:
    # Mapeia as linhas de dados dentro do tbody da tabela
    linhas = ctx.locator("table[name='paginationTable'] tbody.scrollBody tr")
    
    try:
        # Aguarda até que a primeira linha esteja visível
        primeira_linha = linhas.first
        primeira_linha.wait_for(state="visible", timeout=timeout_ms)
        
        total_linhas = linhas.count()
        logger.info("Tabela carregada com sucesso. Total de linhas: {}", total_linhas)
        
        # Localiza o botão anexar dentro da primeira linha
        botao_anexar = primeira_linha.locator("[name='anexar'], input[name='anexar'], button[name='anexar']").first
        botao_anexar.wait_for(state="visible", timeout=timeout_ms)
        
        # Clica no botão anexar com suporte a AJAX
        clicar_com_ajax(ctx, botao_anexar)
        return True

    except PlaywrightTimeoutError:
        logger.warning("Nenhuma linha encontrada após {}ms. Clicando em Cancelar...", timeout_ms)
        
        # Clica no botão Cancelar caso não encontre nenhuma linha
        clicar_com_ajax(ctx, "button[name='submitCancel']")
        return False
        
    except Exception as e:
        logger.error("Erro inesperado ao aguardar/clicar na tabela: {}", e)
        # Em caso de outro erro inesperado, também tenta cancelar para não travar o fluxo
        try:
            clicar_com_ajax(ctx, "button[name='submitCancel']")
        except Exception:
            pass
        return False


def _preencher(ctx, linha: int) -> None:
    # Corrigido de input para button
    clicar_com_ajax(ctx, f"button[name='lookup-patrimonio-{linha}-7']")
    clicar_com_ajax(ctx, "button[name='submitSearch']")
    clicar_primeira_linha_se_existir(ctx)