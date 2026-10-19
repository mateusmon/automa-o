from loguru import logger
from playwright.sync_api import Page

from flows.patrimonio.termo_responsabilidade.recebimento_termo_responsabilidade.consulta_recebimento_termo_responsabilidade.consultar_recebimento_termo_responsabilidade_flow import consultar_recebimento_termo_responsabilidade
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro

def preencher_dados_gerais(page: Page, ug: dict[str, str]) -> bool:
    logger.info("Preenchendo dados gerais {}.".format(ug["codigo"]))

    ctx = escopo(page)

    has_termo = consultar_recebimento_termo_responsabilidade(page, ug)

    if not has_termo:
        return False
    
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Dados gerais preenchidos {}.".format(ug["codigo"]))

    return True